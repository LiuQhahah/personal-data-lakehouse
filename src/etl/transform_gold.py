"""
Gold Layer - 数据聚合
基于Silver层数据进行业务汇总
"""
import pandas as pd
from datetime import datetime
import os

BASE_DIR = "/Users/qiang_liu/workspace/personal-lakehouse/data"
SILVER_DIR = f"{BASE_DIR}/warehouse/silver"
GOLD_DIR = f"{BASE_DIR}/warehouse/gold"
os.makedirs(GOLD_DIR, exist_ok=True)

def create_github_gold():
    """GitHub数据聚合"""
    df = pd.read_parquet(f"{SILVER_DIR}/github_repos_silver.parquet")
    
    # 1. 语言统计
    lang_stats = df.groupby("language").agg({
        "repo_name": "count",
        "stars": "sum",
        "forks": "sum"
    }).rename(columns={"repo_name": "repo_count"})
    lang_stats = lang_stats.sort_values("stars", ascending=False)
    lang_stats.to_parquet(f"{GOLD_DIR}/github_language_stats.parquet")
    print(f"GitHub语言统计: {len(lang_stats)} 种")
    
    # 2. 主题分类统计 (新增)
    theme_stats = df.groupby("theme").agg({
        "repo_name": "count",
        "stars": "sum"
    }).rename(columns={"repo_name": "repo_count"})
    theme_stats = theme_stats.sort_values("stars", ascending=False)
    theme_stats.to_parquet(f"{GOLD_DIR}/github_theme_stats.parquet")
    print(f"GitHub主题分类: {len(theme_stats)} 种")
    
    # 3. Top 10 仓库
    top_repos = df.nlargest(10, "stars")[["repo_name", "language", "stars", "forks", "owner", "theme"]]
    top_repos.to_parquet(f"{GOLD_DIR}/github_top10.parquet", index=False)
    print(f"GitHub Top10: {len(top_repos)} repos")
    
    # 4. 许可证统计 (新增)
    license_stats = df.groupby("license").agg({
        "repo_name": "count"
    }).rename(columns={"repo_name": "repo_count"})
    license_stats = license_stats[license_stats.index != ""].sort_values("repo_count", ascending=False)
    license_stats.to_parquet(f"{GOLD_DIR}/github_license_stats.parquet")
    print(f"GitHub许可证: {len(license_stats)} 种")
    
    # 5. Owner类型统计 (新增)
    owner_stats = df.groupby("owner_type").agg({
        "repo_name": "count",
        "stars": "sum"
    }).rename(columns={"repo_name": "repo_count"})
    owner_stats.to_parquet(f"{GOLD_DIR}/github_owner_stats.parquet")
    print(f"GitHub Owner类型: {len(owner_stats)} 种")
    
    # 6. 总体统计
    total_stats = pd.DataFrame([{
        "total_repos": len(df),
        "total_stars": df["stars"].sum(),
        "total_forks": df["forks"].sum(),
        "avg_stars": round(df["stars"].mean(), 0),
        "median_stars": df["stars"].median(),
        "top_language": df["language"].mode()[0] if len(df["language"].mode()) > 0 else "N/A",
        "top_theme": df["theme"].mode()[0] if len(df["theme"].mode()) > 0 else "N/A"
    }])
    total_stats.to_parquet(f"{GOLD_DIR}/github_overall_stats.parquet", index=False)
    print(f"GitHub总体: {total_stats['total_repos'][0]} repos")

def create_bilibili_gold():
    """B站数据聚合"""
    df = pd.read_parquet(f"{SILVER_DIR}/bilibili_videos_silver.parquet")
    
    # 1. 热门作者 Top 10
    author_stats = df.groupby("author").agg({
        "title": "count",
        "view": "sum",
        "like": "sum"
    }).rename(columns={"title": "video_count"}).sort_values("view", ascending=False).head(10)
    author_stats.to_parquet(f"{GOLD_DIR}/bilibili_top_authors.parquet")
    print(f"B站热门作者: {len(author_stats)} 位")
    
    # 2. 分类统计
    cat_stats = df.groupby("category").agg({
        "title": "count",
        "view": "sum"
    }).rename(columns={"title": "video_count"}).sort_values("view", ascending=False)
    cat_stats.to_parquet(f"{GOLD_DIR}/bilibili_category_stats.parquet")
    print(f"B站分类: {len(cat_stats)} 种")
    
    # 3. 播放量分段
    view_bins = pd.cut(
        df["view"],
        bins=[0, 100000, 500000, 1000000, 5000000, 100000000],
        labels=["<10万", "10-50万", "50-100万", "100-500万", "500万+"]
    )
    view_dist = df.groupby(view_bins, observed=False).size()
    view_dist_df = view_dist.reset_index(name="video_count")
    view_dist_df.to_parquet(f"{GOLD_DIR}/bilibili_view_dist.parquet", index=False)
    print(f"B站播放分布: {len(view_dist)} 档")
    
    # 4. 总体统计
    total_stats = pd.DataFrame([{
        "total_videos": len(df),
        "total_views": df["view"].sum(),
        "total_likes": df["like"].sum(),
        "total_replies": df["reply"].sum(),
        "avg_views": round(df["view"].mean(), 0),
        "avg_likes": round(df["like"].mean(), 0),
        "avg_engagement": round(df["engagement_rate"].mean(), 2)
    }])
    total_stats.to_parquet(f"{GOLD_DIR}/bilibili_overall_stats.parquet", index=False)
    print(f"B站总体: {total_stats['total_videos'][0]} videos")

if __name__ == "__main__":
    print("=" * 50)
    print("Gold Layer Aggregation (with Theme Stats)")
    print("=" * 50)
    
    create_github_gold()
    print()
    create_bilibili_gold()
    
    print("\nDone!")
