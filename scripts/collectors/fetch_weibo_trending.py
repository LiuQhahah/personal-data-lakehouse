#!/usr/bin/env python3
"""
微博热搜数据采集脚本
Collects Weibo trending data

Usage:
    python fetch_weibo_trending.py [--output /path/to/output.json]
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import urllib.request
import ssl

# 忽略 SSL 警告
ssl._create_default_https_context = ssl._create_unverified_context


class WeiboCollector:
    """微博热搜采集器"""
    
    # 公开的微博热搜 API (非官方，仅供参考)
    API_URL = "https://weibo.com/ajax/statuses/hot"
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://weibo.com",
        }
    
    def fetch(self) -> List[Dict[str, Any]]:
        """
        获取微博热搜数据
        
        Returns:
            List of trending items
        """
        print(f"[Weibo] Fetching trending data...")
        
        try:
            request = urllib.request.Request(
                self.API_URL,
                headers=self.headers
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if data.get('ok') == 1:
                raw_data = data.get('data', {}).get('realtime', [])
                
                results = []
                for item in raw_data:
                    results.append({
                        'rank_value': item.get('rank', 0),
                        'keyword': item.get('word', ''),
                        'hot_level': item.get('label_name', ''),
                        'hot_value': item.get('num', 0),
                        'url': f"https://s.weibo.com/weibo?q={item.get('word', '')}",
                        'category': item.get('category', ''),
                        'fetch_time': datetime.now().isoformat(),
                    })
                
                print(f"[Weibo] Found {len(results)} trending items")
                return results
            else:
                print(f"[Weibo] API returned error: {data}")
                return []
                
        except Exception as e:
            print(f"[Weibo] Error fetching data: {e}")
            return []
    
    def fetch_alternative(self) -> List[Dict[str, Any]]:
        """
        备选方案：使用第三方API
        """
        # 尝试多个公开 API
        alternative_apis = [
            "https://weibo.com/ajax/side/hotSearch",
            "https://weibo.com/ajax/statuses/mymblog?uid=&feature=0&is_all=1",
        ]
        
        for api in alternative_apis:
            try:
                request = urllib.request.Request(api, headers=self.headers)
                with urllib.request.urlopen(request, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"[Weibo] Tried {api}, result: {data.get('ok')}")
            except Exception as e:
                print(f"[Weibo] Failed {api}: {e}")
                continue
        
        return []


def save_to_file(data: List[Dict], output_path: str):
    """保存数据到文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'count': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[Weibo] Data saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Weibo Trending Collector')
    parser.add_argument('--output', default='./data/weibo_trending.json',
                        help='Output file path')
    parser.add_argument('--test', action='store_true',
                        help='Test mode - just print result')
    
    args = parser.parse_args()
    
    collector = WeiboCollector()
    data = collector.fetch()
    
    if args.test:
        print(f"\n[TEST] Raw data preview:")
        print(json.dumps(data[:3], ensure_ascii=False, indent=2))
        return
    
    if data:
        save_to_file(data, args.output)
    else:
        print("[Weibo] No data collected")
        sys.exit(1)


if __name__ == '__main__':
    main()