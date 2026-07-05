#!/usr/bin/env python3
"""
GitHub Trending 数据采集脚本
Uses GitHub REST API v3

Usage:
    # 确保 ~/.lakehouse_env 包含 GITHUB_TOKEN
    python fetch_github_trending.py
"""

import os
import sys
import json
import argparse
import urllib.request
import ssl
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_github_token

# 禁用 SSL 验证警告
ssl._create_default_https_context = ssl._create_unverified_context


class GitHubTrendingCollector:
    """GitHub Trending 采集器"""
    
    SEARCH_API = "https://api.github.com/search/repositories"
    
    def __init__(self, token: str = None):
        self.token = token or get_github_token()
        
        self.headers = {
            "User-Agent": "GitHub-Trending-Collector/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            print("[GitHub] ✓ Using authenticated token")
        else:
            print("[GitHub] ✗ No token, rate limited")
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """发起 API 请求"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
                elif response.status == 403:
                    print("[GitHub] Rate limited!")
                    return None
                else:
                    print(f"[GitHub] HTTP {response.status}")
                    return None
                    
        except Exception as e:
            print(f"[GitHub] Request error: {e}")
            return None
    
    def fetch(self, language: str = None, since: str = "daily", 
              min_stars: int = 100) -> List[Dict[str, Any]]:
        """
        获取 GitHub 热门仓库
        """
        # 构建查询
        query = f"stars:>{min_stars}"
        if language:
            query += f" language:{language}"
        
        # 时间过滤 (可选，暂时不过滤以获取更多结果)
        # 热门仓库通常是历史积累的，不按创建时间过滤
        # days = {"daily": 1, "weekly": 7, "monthly": 30}.get(since, 1)
        # date_str = (date.today() - timedelta(days=days)).isoformat()
        # query += f" created:>={date_str}"
        
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 30,
        }
        
        query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        url = f"{self.SEARCH_API}?{query_string}"
        
        print(f"[GitHub] Fetching: {language or 'all'} ({since}), stars>{min_stars}")
        
        result = self._make_request(url)
        
        if not result or 'items' not in result:
            print("[GitHub] No results")
            return []
        
        repos = []
        for item in result['items'][:30]:
            repos.append({
                'repo_name': item.get('full_name', ''),
                'description': (item.get('description') or '')[:200],
                'language': item.get('language', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'today_stars': 0,
                'contributors': item.get('open_issues_count', 0),
                'url': item.get('html_url', ''),
                'fetch_date': date.today().isoformat(),
                'created_at': item.get('created_at', ''),
                'topics': item.get('topics', []),  # 新增: GitHub主题标签
                'license': (item.get('license') or {}).get('spdx_id', ''),  # 新增: 开源许可证
                'owner_type': (item.get('owner') or {}).get('type', ''),  # 新增: Owner类型(User/Organization)
            })
        
        print(f"[GitHub] ✓ Found {len(repos)} repos")
        return repos


def save_to_file(data: List[Dict], output_path: str):
    """保存数据到文件"""
    output_dir = os.path.dirname(output_path) or '.'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'fetch_time': datetime.now().isoformat(),
            'count': len(data),
            'data': data
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[GitHub] ✓ Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='GitHub Trending Collector')
    parser.add_argument('--language', '-l', default=None)
    parser.add_argument('--since', '-s', default='daily',
                        choices=['daily', 'weekly', 'monthly'])
    parser.add_argument('--min-stars', '-m', type=int, default=100)
    parser.add_argument('--output', '-o', default='./data/github_trending.json')
    parser.add_argument('--test', action='store_true')
    
    args = parser.parse_args()
    
    collector = GitHubTrendingCollector()
    data = collector.fetch(
        language=args.language,
        since=args.since,
        min_stars=args.min_stars
    )
    
    if args.test:
        print(f"\n[TEST] First 5 repos:")
        for repo in data[:5]:
            print(f"  ★ {repo['stars']:>5} | {repo['repo_name']:<40} | {repo['language'] or 'N/A'}")
        return
    
    if data:
        save_to_file(data, args.output)
    else:
        print("[GitHub] ✗ No data")
        sys.exit(1)


if __name__ == '__main__':
    main()