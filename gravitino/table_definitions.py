#!/usr/bin/env python3
"""
Lakehouse 表定义
所有的 Iceberg 表定义，用于 Gravitino Schema Registry

这些定义对应 sql/create_tables.sql 中的表结构
"""

# ============================================================
# BRONZE LAYER 表定义
# ============================================================

BRONZE_TABLES = {
    "bronze_github_trending": {
        "comment": "GitHub Trending 原始数据",
        "columns": [
            {"name": "repo_name", "type": "string", "nullable": False, "comment": "完整仓库名"},
            {"name": "description", "type": "string", "nullable": True, "comment": "仓库描述"},
            {"name": "language", "type": "string", "nullable": True, "comment": "编程语言"},
            {"name": "stars", "type": "int", "nullable": False, "comment": "星星数"},
            {"name": "forks", "type": "int", "nullable": False, "comment": "Fork数"},
            {"name": "today_stars", "type": "int", "nullable": False, "comment": "今日新增星星"},
            {"name": "contributors", "type": "int", "nullable": False, "comment": "贡献者数"},
            {"name": "url", "type": "string", "nullable": False, "comment": "GitHub链接"},
            {"name": "fetch_date", "type": "date", "nullable": False, "comment": "采集日期"},
            {"name": "created_at", "type": "timestamp", "nullable": True, "comment": "仓库创建时间"},
            {"name": "_raw_json", "type": "string", "nullable": True, "comment": "原始JSON"},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False, "comment": "摄入时间"},
            {"name": "_batch_id", "type": "string", "nullable": False, "comment": "批次ID"},
        ],
        "partitioning": [{"field": "fetch_date", "transform": "day"}],
        "properties": {
            "format-version": "2",
            "write.distribution-mode": "hash"
        }
    },
    
    "bronze_bilibili_trending": {
        "comment": "B站热搜原始数据",
        "columns": [
            {"name": "rank_value", "type": "int", "nullable": False, "comment": "排名"},
            {"name": "title", "type": "string", "nullable": False, "comment": "视频标题"},
            {"name": "description", "type": "string", "nullable": True, "comment": "描述"},
            {"name": "url", "type": "string", "nullable": False, "comment": "视频链接"},
            {"name": "bvid", "type": "string", "nullable": False, "comment": "B站视频ID"},
            {"name": "author", "type": "string", "nullable": True, "comment": "UP主"},
            {"name": "view_count", "type": "bigint", "nullable": False, "comment": "播放量"},
            {"name": "like_count", "type": "bigint", "nullable": False, "comment": "点赞数"},
            {"name": "reply_count", "type": "bigint", "nullable": False, "comment": "评论数"},
            {"name": "category", "type": "string", "nullable": False, "comment": "分类"},
            {"name": "fetch_time", "type": "timestamp", "nullable": False, "comment": "采集时间"},
            {"name": "_raw_json", "type": "string", "nullable": True, "comment": "原始JSON"},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False, "comment": "摄入时间"},
            {"name": "_batch_id", "type": "string", "nullable": False, "comment": "批次ID"},
        ],
        "partitioning": [{"field": "fetch_time", "transform": "hour"}],
        "properties": {
            "format-version": "2"
        }
    },
    
    "bronze_youtube_watches": {
        "comment": "YouTube 观看历史 (Takeout)",
        "columns": [
            {"name": "header", "type": "string", "nullable": True, "comment": "数据头"},
            {"name": "title", "type": "string", "nullable": True, "comment": "视频标题"},
            {"name": "titleUrl", "type": "string", "nullable": True, "comment": "视频URL"},
            {"name": "time", "type": "string", "nullable": True, "comment": "观看时间"},
            {"name": "subtitles", "type": "string", "nullable": True, "comment": "频道信息"},
            {"name": "details", "type": "string", "nullable": True, "comment": "额外详情"},
            {"name": "imports", "type": "string", "nullable": True, "comment": "导入来源"},
            {"name": "_raw_json", "type": "string", "nullable": True, "comment": "完整原始JSON"},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False, "comment": "摄入时间"},
            {"name": "_batch_id", "type": "string", "nullable": False, "comment": "批次ID"},
            {"name": "_source_file", "type": "string", "nullable": True, "comment": "原始文件名"},
        ],
        "partitioning": [{"field": "_ingest_time", "transform": "year"}],
        "properties": {}
    },
    
    "bronze_chrome_history": {
        "comment": "Chrome 浏览器历史 (Takeout)",
        "columns": [
            {"name": "browser_name", "type": "string", "nullable": True},
            {"name": "datetime", "type": "string", "nullable": True},
            {"name": "url", "type": "string", "nullable": True},
            {"name": "title", "type": "string", "nullable": True},
            {"name": "visits", "type": "string", "nullable": True},
            {"name": "_raw_json", "type": "string", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_batch_id", "type": "string", "nullable": False},
            {"name": "_source_file", "type": "string", "nullable": True},
        ],
        "partitioning": [{"field": "_ingest_time", "transform": "year"}],
        "properties": {}
    },
    
    "bronze_github_events": {
        "comment": "GitHub 事件 (Webhook)",
        "columns": [
            {"name": "event_id", "type": "string", "nullable": False},
            {"name": "event_type", "type": "string", "nullable": False},
            {"name": "actor", "type": "string", "nullable": True},
            {"name": "repo", "type": "string", "nullable": True},
            {"name": "payload", "type": "string", "nullable": True},
            {"name": "public_flag", "type": "boolean", "nullable": False},
            {"name": "created_at", "type": "string", "nullable": True},
            {"name": "_raw_json", "type": "string", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_batch_id", "type": "string", "nullable": False},
            {"name": "_source", "type": "string", "nullable": True},
        ],
        "partitioning": [{"field": "_ingest_time", "transform": "month"}],
        "properties": {}
    }
}

# ============================================================
# SILVER LAYER 表定义
# ============================================================

SILVER_TABLES = {
    "silver_github_trending": {
        "comment": "GitHub Trending 清洗后数据",
        "columns": [
            {"name": "rank_value", "type": "int", "nullable": False, "comment": "排名"},
            {"name": "repo_name", "type": "string", "nullable": False, "comment": "仓库名"},
            {"name": "repo_owner", "type": "string", "nullable": True, "comment": "仓库所有者"},
            {"name": "repo_name_only", "type": "string", "nullable": True, "comment": "仅仓库名"},
            {"name": "description", "type": "string", "nullable": True, "comment": "描述"},
            {"name": "description_length", "type": "int", "nullable": True, "comment": "描述长度"},
            {"name": "language", "type": "string", "nullable": True, "comment": "语言"},
            {"name": "stars", "type": "int", "nullable": False, "comment": "星星数"},
            {"name": "forks", "type": "int", "nullable": False, "comment": "Forks"},
            {"name": "today_stars", "type": "int", "nullable": False},
            {"name": "contributors", "type": "int", "nullable": False},
            {"name": "url", "type": "string", "nullable": False},
            {"name": "fetch_date", "type": "date", "nullable": False},
            {"name": "created_at", "type": "timestamp", "nullable": True},
            {"name": "is_starred_above_100k", "type": "boolean", "nullable": True},
            {"name": "is_starred_above_50k", "type": "boolean", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_batch_id", "type": "string", "nullable": False},
        ],
        "partitioning": [
            {"field": "fetch_date", "transform": "year"},
            {"field": "fetch_date", "transform": "month"}
        ],
        "properties": {"format-version": "2"}
    },
    
    "silver_bilibili_trending": {
        "comment": "B站热搜清洗后数据",
        "columns": [
            {"name": "rank_value", "type": "int", "nullable": False},
            {"name": "title", "type": "string", "nullable": False},
            {"name": "title_length", "type": "int", "nullable": True},
            {"name": "has_description", "type": "boolean", "nullable": True},
            {"name": "description", "type": "string", "nullable": True},
            {"name": "url", "type": "string", "nullable": False},
            {"name": "bvid", "type": "string", "nullable": False},
            {"name": "author", "type": "string", "nullable": True},
            {"name": "view_count", "type": "bigint", "nullable": False},
            {"name": "like_count", "type": "bigint", "nullable": False},
            {"name": "reply_count", "type": "bigint", "nullable": False},
            {"name": "comment_rate", "type": "double", "nullable": True},
            {"name": "category", "type": "string", "nullable": False},
            {"name": "fetch_time", "type": "timestamp", "nullable": False},
            {"name": "fetch_date", "type": "date", "nullable": True},
            {"name": "fetch_hour", "type": "int", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_batch_id", "type": "string", "nullable": False},
        ],
        "partitioning": [
            {"field": "fetch_time", "transform": "year"},
            {"field": "fetch_time", "transform": "month"},
            {"field": "fetch_time", "transform": "day"}
        ],
        "properties": {"format-version": "2"}
    },
    
    "silver_youtube_watches": {
        "comment": "YouTube 观看历史清洗后",
        "columns": [
            {"name": "video_id", "type": "string", "nullable": True},
            {"name": "video_title", "type": "string", "nullable": True},
            {"name": "channel_id", "type": "string", "nullable": True},
            {"name": "channel_name", "type": "string", "nullable": True},
            {"name": "watch_timestamp", "type": "timestamp", "nullable": True},
            {"name": "watch_date", "type": "date", "nullable": True},
            {"name": "watch_hour", "type": "int", "nullable": True},
            {"name": "watch_dayofweek", "type": "string", "nullable": True},
            {"name": "watch_month", "type": "string", "nullable": True},
            {"name": "watch_year", "type": "int", "nullable": True},
            {"name": "url", "type": "string", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_source_file", "type": "string", "nullable": True},
            {"name": "_batch_id", "type": "string", "nullable": False},
        ],
        "partitioning": [
            {"field": "watch_timestamp", "transform": "year"},
            {"field": "watch_timestamp", "transform": "month"}
        ],
        "properties": {"format-version": "2"}
    },
    
    "silver_chrome_history": {
        "comment": "Chrome 历史清洗后",
        "columns": [
            {"name": "url", "type": "string", "nullable": True},
            {"name": "domain", "type": "string", "nullable": True},
            {"name": "title", "type": "string", "nullable": True},
            {"name": "visit_time", "type": "timestamp", "nullable": True},
            {"name": "visit_date", "type": "date", "nullable": True},
            {"name": "visit_hour", "type": "int", "nullable": True},
            {"name": "visit_dayofweek", "type": "string", "nullable": True},
            {"name": "visit_month", "type": "string", "nullable": True},
            {"name": "visit_year", "type": "int", "nullable": True},
            {"name": "visit_count", "type": "int", "nullable": True},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_source_file", "type": "string", "nullable": True},
            {"name": "_batch_id", "type": "string", "nullable": False},
        ],
        "partitioning": [
            {"field": "visit_time", "transform": "year"},
            {"field": "visit_time", "transform": "month"}
        ],
        "properties": {}
    },
    
    "silver_github_events": {
        "comment": "GitHub 事件清洗后",
        "columns": [
            {"name": "event_id", "type": "string", "nullable": False},
            {"name": "event_type", "type": "string", "nullable": False},
            {"name": "actor_login", "type": "string", "nullable": True},
            {"name": "actor_id", "type": "bigint", "nullable": True},
            {"name": "repo_name", "type": "string", "nullable": True},
            {"name": "repo_id", "type": "bigint", "nullable": True},
            {"name": "action", "type": "string", "nullable": True},
            {"name": "created_at", "type": "timestamp", "nullable": True},
            {"name": "created_date", "type": "date", "nullable": True},
            {"name": "created_hour", "type": "int", "nullable": True},
            {"name": "payload_json", "type": "string", "nullable": True},
            {"name": "is_public", "type": "boolean", "nullable": False},
            {"name": "_ingest_time", "type": "timestamp", "nullable": False},
            {"name": "_batch_id", "type": "string", "nullable": False},
        ],
        "partitioning": [
            {"field": "created_at", "transform": "year"},
            {"field": "created_at", "transform": "month"}
        ],
        "properties": {}
    }
}

# ============================================================
# GOLD LAYER 表定义
# ============================================================

GOLD_TABLES = {
    "gold_github_monthly_stats": {
        "comment": "GitHub 月度统计",
        "columns": [
            {"name": "year_month", "type": "string", "nullable": False},
            {"name": "total_events", "type": "bigint", "nullable": False},
            {"name": "total_commits", "type": "bigint", "nullable": False},
            {"name": "total_prs", "type": "bigint", "nullable": False},
            {"name": "total_issues", "type": "bigint", "nullable": False},
            {"name": "total_stars", "type": "bigint", "nullable": False},
            {"name": "repos_contributed", "type": "string", "nullable": True},
            {"name": "active_days", "type": "int", "nullable": False},
            {"name": "streak_days", "type": "int", "nullable": False},
            {"name": "most_active_hour", "type": "int", "nullable": True},
            {"name": "_computed_at", "type": "timestamp", "nullable": False},
        ],
        "partitioning": [{"field": "_computed_at", "transform": "year"}],
        "properties": {}
    },
    
    "gold_youtube_monthly_stats": {
        "comment": "YouTube 月度观看统计",
        "columns": [
            {"name": "year_month", "type": "string", "nullable": False},
            {"name": "total_watches", "type": "int", "nullable": False},
            {"name": "unique_videos", "type": "int", "nullable": False},
            {"name": "unique_channels", "type": "int", "nullable": False},
            {"name": "top_10_channels", "type": "string", "nullable": True},
            {"name": "total_watch_minutes", "type": "bigint", "nullable": False},
            {"name": "avg_daily_watches", "type": "double", "nullable": False},
            {"name": "most_active_hour", "type": "int", "nullable": True},
            {"name": "most_active_day", "type": "string", "nullable": True},
            {"name": "_computed_at", "type": "timestamp", "nullable": False},
            {"name": "_date_range_start", "type": "date", "nullable": True},
            {"name": "_date_range_end", "type": "date", "nullable": True},
        ],
        "partitioning": [{"field": "_computed_at", "transform": "year"}],
        "properties": {}
    }
}


# 导出所有表定义
ALL_TABLES = {
    **BRONZE_TABLES,
    **SILVER_TABLES,
    **GOLD_TABLES
}


def get_table_definition(table_name: str) -> dict:
    """获取表定义"""
    return ALL_TABLES.get(table_name)


def list_all_tables() -> list:
    """列出所有表名"""
    return list(ALL_TABLES.keys())


def get_tables_by_layer(layer: str) -> dict:
    """按层级获取表"""
    if layer == "bronze":
        return BRONZE_TABLES
    elif layer == "silver":
        return SILVER_TABLES
    elif layer == "gold":
        return GOLD_TABLES
    return {}


# 测试
if __name__ == "__main__":
    print("Lakehouse 表定义")
    print("=" * 40)
    print(f"Bronze: {len(BRONZE_TABLES)} 张表")
    print(f"Silver: {len(SILVER_TABLES)} 张表")
    print(f"Gold: {len(GOLD_TABLES)} 张表")
    print(f"总计: {len(ALL_TABLES)} 张表")
    print()
    print("表列表:")
    for name in ALL_TABLES:
        print(f"  - {name}")