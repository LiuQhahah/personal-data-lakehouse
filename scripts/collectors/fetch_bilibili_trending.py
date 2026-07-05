#!/usr/bin/env python3
"""
B站热搜数据采集脚本 (使用 curl)
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import List, Dict, Any


class BilibiliTrendingCollector:
    """B站热搜采集器 - 使用 curl"""
    
    API_URL = "https://api.bilibili.com/x/web-interface/ranking/v2"
    
    CATEGORIES = {
        "all": 0,
        "douga": 1,
        "music": 3,
        "game": 4,
        "tech": 36,
        "life": 160,
    }
    
    def fetch(self, category: str = "all") -> List[Dict[str, Any]]:
        """使用 curl 获取数据"""
        
        rid = self.CATEGORIES.get(category, 0)
        url = f"{self.API_URL}?rid={rid}&type=all"
        
        print(f"[Bilibili] Fetching: {category}")
        
        try:
            # 使用 curl 调用
            cmd = [
                'curl', '-s',
                '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '-H', 'Referer: https://www.bilibili.com',
                '-H', 'Accept: application/json',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            data = json.loads(result.stdout.decode('utf-8'))
            
            code = data.get('code', -1)
            
            if code != 0:
                print(f"[Bilibili] API Error: {data.get('message')}")
                return []
            
            items = data.get('data', {}).get('list', [])
            
            results = []
            for idx, item in enumerate(items, 1):
                results.append({
                    'rank': idx,
                    'title': item.get('title', ''),
                    'description': item.get('desc', ''),
                    'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    'bvid': item.get('bvid', ''),
                    'author': item.get('owner', {}).get('name', ''),
                    'view': item.get('stat', {}).get('view', 0),
                    'like': item.get('stat', {}).get('like', 0),
                    'reply': item.get('stat', {}).get('reply', 0),
                    'category': category,
                    'fetch_time': datetime.now().isoformat(),
                })
            
            print(f"[Bilibili] ✓ Found {len(results)} items")
            return results
            
        except Exception as e:
            print(f"[Bilibili] Error: {e}")
            return []


def save_to_file(data: List[Dict], output_path: str):
    """保存数据"""
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'count': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[Bilibili] ✓ Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Bilibili Collector')
    parser.add_argument('--category', '-c', default='all')
    parser.add_argument('--output', '-o', default='./data/bilibili_trending.json')
    parser.add_argument('--test', action='store_true')
    
    args = parser.parse_args()
    
    collector = BilibiliTrendingCollector()
    data = collector.fetch(args.category)
    
    if args.test:
        print(f"\n[TEST] First 5:")
        for item in data[:5]:
            print(f"  {item.get('rank')}. {item.get('title', '')[:40]}")
        return
    
    if data:
        save_to_file(data, args.output)
    else:
        print("[Bilibili] ✗ No data")
        sys.exit(1)


if __name__ == '__main__':
    main()