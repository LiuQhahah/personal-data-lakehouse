#!/usr/bin/env python3
"""
A股数据采集脚本
Collects China A-share stock data using akshare

Usage:
    python fetch_stock_cn.py [--index] [--output /path/to/output.json]
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("Warning: akshare not installed. Install with: pip install akshare")


class StockCNCollector:
    """A股数据采集器"""
    
    def __init__(self):
        pass
    
    def fetch_index_spot(self) -> List[Dict[str, Any]]:
        """
        获取A股大盘指数实时行情
        上证指数、深证成指、创业板指等
        """
        if not AKSHARE_AVAILABLE:
            return []
        
        print("[Stock CN] Fetching A-share index spot...")
        
        try:
            df = ak.stock_zh_index_spot()
            
            results = []
            for _, row in df.iterrows():
                # 过滤主要指数
                if row.get('代码') in ['000001', '399001', '399006', '000300', '000016']:
                    results.append({
                        'symbol': row.get('代码'),
                        'name': row.get('名称'),
                        'market': 'CN',
                        'price': self._parse_float(row.get('最新价')),
                        'change_pct': self._parse_float(row.get('涨跌幅')),
                        'volume': self._parse_int(row.get('成交量')),
                        'amount': self._parse_float(row.get('成交额')),
                        'high': self._parse_float(row.get('最高')),
                        'low': self._parse_float(row.get('最低')),
                        'open_price': self._parse_float(row.get('今开')),
                        'pre_close': self._parse_float(row.get('昨收')),
                        'trade_time': datetime.now().isoformat(),
                    })
            
            print(f"[Stock CN] Retrieved {len(results)} indices")
            return results
            
        except Exception as e:
            print(f"[Stock CN] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def fetch_stock_spot(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        获取个股实时行情
        """
        if not AKSHARE_AVAILABLE:
            return []
        
        if not symbols:
            symbols = ['000001', '000002', '600000']  # 平安、银行、浦发
        
        print(f"[Stock CN] Fetching {len(symbols)} stocks...")
        
        results = []
        
        for symbol in symbols:
            try:
                df = ak.stock_zh_a_spot_em()
                
                # 筛选指定股票
                stock = df[df['代码'] == symbol]
                
                if not stock.empty:
                    row = stock.iloc[0]
                    results.append({
                        'symbol': symbol,
                        'name': row.get('名称'),
                        'market': 'CN',
                        'price': self._parse_float(row.get('最新价')),
                        'change_pct': self._parse_float(row.get('涨跌幅')),
                        'volume': self._parse_int(row.get('成交量')),
                        'amount': self._parse_float(row.get('成交额')),
                        'high': self._parse_float(row.get('最高')),
                        'low': self._parse_float(row.get('最低')),
                        'open_price': self._parse_float(row.get('今开')),
                        'pre_close': self._parse_float(row.get('昨收')),
                        'trade_time': datetime.now().isoformat(),
                    })
                    
            except Exception as e:
                print(f"[Stock CN] Error fetching {symbol}: {e}")
        
        return results
    
    @staticmethod
    def _parse_float(val):
        """安全解析浮点数"""
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _parse_int(val):
        """安全解析整数"""
        if val is None:
            return None
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None


def save_to_file(data: List[Dict], output_path: str):
    """保存数据到文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'count': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[Stock CN] Data saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='China A-Share Stock Collector')
    parser.add_argument('--index', action='store_true',
                        help='Fetch index (大盘指数)')
    parser.add_argument('--stocks', default=None,
                        help='Comma-separated stock codes (e.g., 000001,600000)')
    parser.add_argument('--output', '-o', default='./data/stock_cn.json',
                        help='Output file path')
    parser.add_argument('--test', action='store_true',
                        help='Test mode')
    
    args = parser.parse_args()
    
    if not AKSHARE_AVAILABLE:
        print("Please install akshare: pip install akshare")
        sys.exit(1)
    
    collector = StockCNCollector()
    
    # 获取大盘指数
    if args.index or (not args.stocks):
        data = collector.fetch_index_spot()
    else:
        # 获取个股
        symbols = [s.strip() for s in args.stocks.split(',')]
        data = collector.fetch_stock_spot(symbols)
    
    if args.test:
        print(f"\n[TEST] Data preview:")
        for item in data[:5]:
            print(f"  - {item.get('name')}: {item.get('price')} ({item.get('change_pct')}%)")
        return
    
    if data:
        save_to_file(data, args.output)
    else:
        print("[Stock CN] No data collected")
        sys.exit(1)


if __name__ == '__main__':
    main()