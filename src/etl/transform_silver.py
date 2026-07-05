"""
Silver Layer - 数据清洗转换
将Bronze层原始数据清洗为标准化格式
"""
import json
import pandas as pd
from datetime import datetime
import os

# 路径配置
BASE_DIR = "/Users/qiang_liu/workspace/personal-lakehouse/data"
BRONZE_DIR = f"{BASE_DIR}/warehouse/bronze"
SILVER_DIR = f"{BASE_DIR}/warehouse/silver"
os.makedirs(SILVER_DIR, exist_ok=True)

def transform_github():
    """清洗GitHub数据"""
    with open(f"{BRONZE_DIR}/github_trending.json") as f:
        raw = json.load(f)
    
    df = pd.DataFrame(raw['data'])
    
    # 数据清洗
    df_clean = df.copy()
    
    # 类型转换
    df_clean['stars'] = pd.to_numeric(df_clean['stars'], errors='coerce').fillna(0).astype(int)
    df_clean['forks'] = pd.to_numeric(df_clean['forks'], errors='coerce').fillna(0).astype(int)
    df_clean['today_stars'] = pd.to_numeric(df_clean['today_stars'], errors='coerce').fillna(0).astype(int)
    df_clean['contributors'] = pd.to_numeric(df_clean['contributors'], errors='coerce').fillna(0).astype(int)
    
    # 日期转换
    df_clean['created_at'] = pd.to_datetime(df_clean['created_at'], errors='coerce')
    df_clean['fetch_date'] = pd.to_datetime(df_clean['fetch_date'], errors='coerce')
    
    # 清理null值
    df_clean['language'] = df_clean['language'].fillna('Unknown')
    df_clean['description'] = df_clean['description'].fillna('').str.strip()
    df_clean['license'] = df_clean['license'].fillna('')
    df_clean['owner_type'] = df_clean['owner_type'].fillna('Unknown')
    
    # 处理topics字段 - 转换为字符串存储
    df_clean['topics'] = df_clean['topics'].apply(
        lambda x: ','.join(x) if isinstance(x, list) else ''
    )
    
    # 添加派生字段
    df_clean['owner'] = df_clean['repo_name'].str.split('/').str[0]
    df_clean['repo'] = df_clean['repo_name'].str.split('/').str[1]
    df_clean['fork_ratio'] = (df_clean['forks'] / df_clean['stars']).round(2)
    df_clean['contributors_per_star'] = (df_clean['contributors'] / df_clean['stars']).round(4)
    
    # 主题分类 - 基于topics关键词
    def categorize_theme(topics_str):
        topics = topics_str.lower().split(',') if topics_str else []
        
        # 定义分类规则
        ai_keywords = ['ai', 'machine-learning', 'ml', 'deep-learning', 'llm', 'gpt', 'llama', 
                      'transformer', 'neural', 'nlp', 'chatgpt', 'openai', 'claude', 'artificial-intelligence']
        frontend_keywords = ['react', 'vue', 'angular', 'javascript', 'typescript', 'css', 
                           'html', 'frontend', 'web', 'ui', 'nodejs', 'node']
        backend_keywords = ['backend', 'api', 'server', 'python', 'django', 'flask', 'go', 
                          'rust', 'java', 'spring', 'database', 'express']
        devops_keywords = ['docker', 'kubernetes', 'k8s', 'devops', 'ci-cd', 'cloud', 
                          'aws', 'infrastructure', 'terraform']
        learning_keywords = ['tutorial', 'education', 'learning', 'course', 'curriculum', 
                           'interview', 'computer-science', 'awesome']
        data_keywords = ['data-science', 'data-analysis', 'pandas', 'numpy', 'tensorflow', 
                        'pytorch', 'statistics', 'analytics']
        
        for t in topics:
            if t in ai_keywords:
                return 'AI/机器学习'
            if t in frontend_keywords:
                return '前端开发'
            if t in backend_keywords:
                return '后端开发'
            if t in devops_keywords:
                return 'DevOps/运维'
            if t in learning_keywords:
                return '学习/教育'
            if t in data_keywords:
                return '数据科学'
        
        return '其他'
    
    df_clean['theme'] = df_clean['topics'].apply(categorize_theme)
    
    # 排序
    df_clean = df_clean.sort_values('stars', ascending=False)
    
    # 保存
    output_path = f"{SILVER_DIR}/github_repos_silver.parquet"
    df_clean.to_parquet(output_path, index=False)
    print(f"GitHub Silver: {len(df_clean)} rows -> {output_path}")
    print(f"  - 新字段: topics, license, owner_type, theme")
    
    return df_clean

def transform_bilibili():
    """清洗B站数据"""
    with open(f"{BRONZE_DIR}/bilibili_trending.json") as f:
        raw = json.load(f)
    
    df = pd.DataFrame(raw['data'])
    
    # 数据清洗
    df_clean = df.copy()
    
    # 类型转换
    df_clean['view'] = pd.to_numeric(df_clean['view'], errors='coerce').fillna(0).astype(int)
    df_clean['like'] = pd.to_numeric(df_clean['like'], errors='coerce').fillna(0).astype(int)
    df_clean['reply'] = pd.to_numeric(df_clean['reply'], errors='coerce').fillna(0).astype(int)
    df_clean['rank'] = pd.to_numeric(df_clean['rank'], errors='coerce').fillna(0).astype(int)
    
    # 日期转换
    df_clean['fetch_time'] = pd.to_datetime(df_clean['fetch_time'], errors='coerce')
    
    # 清理null值
    df_clean['title'] = df_clean['title'].fillna('').str.strip()
    df_clean['description'] = df_clean['description'].fillna('').str.strip()
    df_clean['author'] = df_clean['author'].fillna('Unknown')
    df_clean['category'] = df_clean['category'].fillna('unknown')
    
    # 添加派生字段
    df_clean['engagement_rate'] = ((df_clean['like'] + df_clean['reply']) / df_clean['view'] * 100).round(2)
    df_clean['title_length'] = df_clean['title'].str.len()
    df_clean['view_wan'] = (df_clean['view'] / 10000).round(1)  # 播放量(万)
    
    # 排序
    df_clean = df_clean.sort_values('rank')
    
    # 保存
    output_path = f"{SILVER_DIR}/bilibili_videos_silver.parquet"
    df_clean.to_parquet(output_path, index=False)
    print(f"Bilibili Silver: {len(df_clean)} rows -> {output_path}")
    
    return df_clean

if __name__ == "__main__":
    print("=" * 50)
    print("Silver Layer Transform (with Theme Classification)")
    print("=" * 50)
    
    github_df = transform_github()
    bilibili_df = transform_bilibili()
    
    print("\nDone!")