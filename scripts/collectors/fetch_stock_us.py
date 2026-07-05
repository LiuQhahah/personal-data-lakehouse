#!/usr/bin/env python3
"""
美股数据采集脚本
Collects US stock data using yfinance

Usage:
    python fetch_stock_us.py [--symbols AAPL,MSFT,GOOGL] [--output /path/to/output.json]
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 尝试导入 yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not installed. Install with: pip install yfinance")


class StockUSCollector:
    """美股数据采集器"""
    
    # 默认关注股票
    DEFAULT_SYMBOLS = [
        'AAPL',    # Apple
        'MSFT',    # Microsoft
        'GOOGL',   # Google
        'AMZN',    # Amazon
        'NVDA',    # NVIDIA
        'META',    # Meta
        'TSLA',    # Tesla
        'BRK-B',   # Berkshire
        'JPM',     # JPMorgan
        'V',       # Visa
    ]
    
    def __init__(self):
        self.session = None
    
    def fetch_single(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取单个股票数据
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取历史数据（当天）
            hist = ticker.history(period="1d")
            
            data = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'market': 'US',
                'price': info.get('currentPrice') or (hist['Close'].iloc[-1] if not hist.empty else None),
                'change_pct': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'amount': info.get('regularMarketDayHigh'),
                'high': info.get('regularMarketDayHigh'),
                'low': info.get('regularMarketDayLow'),
                'open_price': info.get('regularMarketOpen'),
                'pre_close': info.get('regularMarketPreviousClose'),
                'trade_time': datetime.now().isoformat(),
            }
            
            print(f"[Stock US] {symbol}: ${data['price']}")
            return data
            
        except Exception as e:
            print(f"[Stock US] Error fetching {symbol}: {e}")
            return None
    
    def fetch(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        获取多个股票数据
        """
        if not YFINANCE_AVAILABLE:
            print("Error: yfinance not available")
            return []
        
        if symbols is None:
            symbols = self.DEFAULT_SYMBOLS
        
        print(f"[Stock US] Fetching {len(symbols)} stocks...")
        
        results = []
        
        # 使用线程池并发获取
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.fetch_single, sym): sym for sym in symbols}
            
            for future in as_completed(futures):
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                except Exception as e:
                    print(f"[Stock US] Error: {e}")
        
        print(f"[Stock US] Retrieved {len(results)} stocks")
        return results
    
    def fetch_market_summary(self) -> Dict[str, Any]:
        """获取市场概览（主要指数）"""
        indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'Dow Jones',
            '^IXIC': 'NASDAQ',
        }
        
        summary = {}
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Open'].iloc[-1]
                    change = ((current - prev) / prev) * 100
                    
                    summary[symbol] = {
                        'name': name,
                        'price': current,
                        'change_pct': change,
                    }
            except Exception as e:
                print(f"[Stock US] Error fetching {symbol}: {e}")
        
        return summary


def save_to_file(data: List[Dict], output_path: str):
    """保存数据到文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'count': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[Stock US] Data saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='US Stock Collector')
    parser.add_argument('--symbols', '-s', default=None,
                        help='Comma-separated stock symbols (default: AAPL,MSFT,GOOGL...)')
    parser.add_argument('--output', '-o', default='./data/stock_us.json',
                        help='Output file path')
    parser.add_argument('--market', action='store_true',
                        help='Also fetch market indices')
    parser.add_argument('--test', action='store_true',
                        help='Test mode')
    
    args = parser.parse_args()
    
    if not YFINANCE_AVAILABLE:
        print("Please install yfinance: pip install yfinance")
        sys.exit(1)
    
    # 解析股票代码
    symbols = None
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    collector = StockUSCollector()
    data = collector.fetch(symbols=symbols)
    
    if args.test:
        print(f"\n[TEST] First 3 stocks:")
        for stock in data[:3]:
            print(f"  - {stock.get('symbol')}: ${stock.get('price')} ({stock.get('change_pct')}%)")
        return
    
    if data:
        save_to_file(data, args.output)
        
        # 如果需要市场指数
        if args.market:
            summary = collector.fetch_market_summary()
            print(f"\n[Market Summary]")
            for symbol, info in summary.items():
                print(f"  {info['name']}: {info['price']:.2f} ({info['change_pct']:.2f}%)")
    else:
        print("[Stock US] No data collected")
        sys.exit(1)


if __name__ == '__main__':
    main()