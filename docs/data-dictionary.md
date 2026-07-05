# Data Dictionary

本文档详细定义了 Personal Data Lakehouse 中所有表的结构。

---

## 1. 命名规范

| 层级 | 命名格式 | 示例 |
|------|---------|------|
| Database | `{project}` | `lakehouse` |
| Table | `{layer}_{source}_{entity}` | `silver_youtube_watches` |
| Column | snake_case | `watch_timestamp` |
| Partition | 按时间分区 | `year=2025/month=06` |

---

## 2. Data Quality Metadata

每张表包含以下元数据列：

| Column | Type | Description |
|--------|------|-------------|
| `_ingest_time` | TIMESTAMP | 数据摄入时间 |
| `_batch_id` | STRING | 批次ID，用于去重 |
| `_source_file` | STRING | 原始文件名 |
| `_dq_status` | STRING | 数据质量状态 (PASS/FAIL) |

---

## 3. TABLE DEFINITIONS

### 3.1 BRONZE LAYER (Raw Data)

#### bronze_github_trending

GitHub Trending 仓库数据 (从 GitHub API 采集)。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `repo_name` | STRING | 完整仓库名 (owner/repo) | "codecrafters-io/build-your-own-x" |
| `description` | STRING | 仓库描述 | "Master programming by recreating..." |
| `language` | STRING | 编程语言 | "Python" |
| `stars` | INT | 星星数 | 512554 |
| `forks` | INT | Fork 数 | 48566 |
| `today_stars` | INT | 今日新增星星 | 0 |
| `contributors` | INT | 贡献者数 | 499 |
| `url` | STRING | GitHub 链接 | "https://github.com/..." |
| `fetch_date` | DATE | 采集日期 | 2026-06-07 |
| `created_at` | TIMESTAMP | 仓库创建时间 | 2018-05-09T12:03:18Z |
| `_raw_json` | STRING | 完整原始JSON | (保留) |
| `_ingest_time` | TIMESTAMP | 摄入时间 | 2026-06-07 09:00:00 |
| `_batch_id` | STRING | 批次ID | "20260607_001" |

**Partition**: `days(fetch_date)`

---

#### bronze_bilibili_trending

B站热搜数据 (从 B站 API 采集)。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `rank_value` | INT | 排名 | 1 |
| `title` | STRING | 视频标题 | "路边一块，也能变废为宝..." |
| `description` | STRING | 描述/简介 | "祝你快乐！" |
| `url` | STRING | 视频链接 | "https://www.bilibili.com/video/..." |
| `bvid` | STRING | B站视频ID | "BV15iEc6VEfH" |
| `author` | STRING | UP主 | "小梨家的和田玉" |
| `view_count` | BIGINT | 播放量 | 5592412 |
| `like_count` | BIGINT | 点赞数 | 211751 |
| `reply_count` | BIGINT | 评论数 | 10559 |
| `category` | STRING | 分类 | "all" |
| `fetch_time` | TIMESTAMP | 采集时间 | 2026-06-07T09:16:48 |
| `_raw_json` | STRING | 完整原始JSON | (保留) |
| `_ingest_time` | TIMESTAMP | 摄入时间 | 2026-06-07 09:16:48 |
| `_batch_id` | STRING | 批次ID | "20260607_001" |

**Partition**: `hours(fetch_time)`

---

#### bronze_youtube_watches

原始 YouTube 观看历史，直接从 Takeout JSON 解析。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `header` | STRING | 数据头，通常为 "YouTube" | "YouTube" |
| `title` | STRING | 视频标题 | "How to build a Lakehouse" |
| `titleUrl` | STRING | 视频URL | "https://youtube.com/watch?v=xxx" |
| `time` | STRING | 观看时间 (ISO 8601) | "2024-01-15T14:30:00Z" |
| `subtitles` | STRING (JSON) | 频道信息 | `[{"name":"ChannelName","url":"..."}]` |
| `details` | STRING (JSON) | 额外详情 | `[]` |
| `header` | STRING (JSON) | 导入来源信息 | `[]` |
| `_raw_json` | STRING | 完整原始JSON | (保留原始数据) |
| `_ingest_time` | TIMESTAMP | 摄入时间 | 2024-01-20 10:00:00 |
| `_batch_id` | STRING | 批次ID | "20240120_001" |
| `_source_file` | STRING | 原始文件名 | "youtube-watch-history.json" |

**Partition**: 不分区（小数据量）  
**Retention**: 永久保留原始数据

---

#### bronze_chrome_history

原始 Chrome 浏览器历史。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `browser_name` | STRING | 浏览器名称 | "Chrome" |
| ` datetime` | STRING | 访问时间 | "2024-01-15 14:30:00" |
| `url` | STRING | 页面URL | "https://github.com/" |
| `title` | STRING | 页面标题 | "GitHub" |
| `visits` | STRING (JSON) | 访问详情 | `[{"time":"..."}]` |
| `_raw_json` | STRING | 完整原始JSON | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | |
| `_source_file` | STRING | 原始文件名 | "BrowserHistory.json" |

**Partition**: 不分区

---

#### bronze_github_events

GitHub 事件的原始 JSON（来自 Webhook 或 API）。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `event_id` | STRING | GitHub Event 唯一ID | "1234567890" |
| `event_type` | STRING | 事件类型 | "PushEvent" |
| `actor` | STRING (JSON) | 触发者信息 | `{"login":"user","id":123}` |
| `repo` | STRING (JSON) | 仓库信息 | `{"name":"user/repo","id":456}` |
| `payload` | STRING (JSON) | 事件负载 | `{"commits":[...]}` |
| `public` | BOOLEAN | 是否公开 | true |
| `created_at` | STRING | 创建时间 (ISO 8601) | "2024-01-15T14:30:00Z" |
| `_raw_json` | STRING | 完整原始JSON | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID (流处理时为时间戳) | |
| `_source` | STRING | 数据来源 | "webhook" / "api" |

**Partition**: 按 `_batch_id` 月分区

---

#### bronze_weibo_trending

微博热搜原始数据。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `rank` | INT | 排名 | 1 |
| `keyword` | STRING | 热词 | "某明星结婚" |
| `hot_level` | STRING | 热度级别 | "爆" |
| `hot_value` | INT | 热度值 | 1234567 |
| `url` | STRING | 热搜链接 | "https://weibo.com/..." |
| `category` | STRING | 分类 | "娱乐" |
| `fetch_time` | TIMESTAMP | 抓取时间 | 2024-01-15 14:00:00 |
| `_raw_json` | STRING | 完整原始JSON | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | "20240115_14" |

**Partition**: 按 `fetch_time` 小时分区

---

#### bronze_twitter_trending

X (Twitter) 热搜原始数据。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `rank` | INT | 排名 | 1 |
| `trend_name` | STRING | 热词 | "#Something" |
| `tweet_volume` | INT | 推文数量 | 50000 |
| `fetch_time` | TIMESTAMP | 抓取时间 | 2024-01-15 14:00:00 |
| `_raw_json` | STRING | 完整原始JSON | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | |

**Partition**: 按 `fetch_time` 小时分区

---

#### bronze_stock_quotations

股票行情数据（A股 + 美股）。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `symbol` | STRING | 股票代码 | "000001" / "AAPL" |
| `name` | STRING | 股票名称 | "平安银行" / "Apple Inc" |
| `market` | STRING | 市场 | "CN" / "US" |
| `price` | DOUBLE | 当前价格 | 150.50 |
| `change_pct` | DOUBLE | 涨跌幅 | 2.35 |
| `volume` | BIGINT | 成交量 | 1000000 |
| `amount` | DOUBLE | 成交额 | 150000000 |
| `high` | DOUBLE | 最高价 | 155.00 |
| `low` | DOUBLE | 最低价 | 148.00 |
| `open` | DOUBLE | 开盘价 | 149.00 |
| `pre_close` | DOUBLE | 昨收价 | 147.00 |
| `trade_time` | TIMESTAMP | 交易时间 | 2024-01-15 15:00:00 |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | "20240115_1500" |

**Partition**: 按 `trade_time` 天分区

---

#### bronze_cctv_news

新闻联播文字版原始数据。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `title` | STRING | 新闻标题 | "习近平发表重要讲话" |
| `content` | STRING | 新闻内容 | (全文) |
| `url` | STRING | 原文链接 | "http://news.cctv.com/..." |
| `publish_time` | TIMESTAMP | 发布时间 | 2024-01-15 19:00:00 |
| `program` | STRING | 节目名称 | "新闻联播" |
| `fetch_time` | TIMESTAMP | 抓取时间 | 2024-01-15 20:00:00 |
| `_raw_html` | STRING | 原始HTML | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | |

**Partition**: 按 `publish_time` 天分区

---

#### bronze_github_trending

GitHub Trending 原始数据。

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `repo_name` | STRING | 仓库名 | "user/repo" |
| `description` | STRING | 仓库描述 | "A cool project" |
| `language` | STRING | 主要语言 | "Python" |
| `stars` | INT | 星标数 | 1000 |
| `forks` | INT | Fork数 | 100 |
| `today_stars` | INT | 今日新增星标 | 50 |
| `contributors` | INT | 贡献者数 | 10 |
| `url` | STRING | 仓库链接 | "https://github.com/..." |
| `fetch_date` | DATE | 抓取日期 | 2024-01-15 |
| `_raw_html` | STRING | 原始HTML | |
| `_ingest_time` | TIMESTAMP | 摄入时间 | |
| `_batch_id` | STRING | 批次ID | |

**Partition**: 按 `fetch_date` 天分区

---

### 3.2 SILVER LAYER (Cleaned Data)

#### silver_youtube_watches

清洗后的 YouTube 观看记录。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `video_id` | STRING | 视频ID (从URL提取) | NO |
| `video_title` | STRING | 视频标题 | NO |
| `channel_id` | STRING | 频道ID | YES |
| `channel_name` | STRING | 频道名称 | YES |
| `watch_timestamp` | TIMESTAMP | 观看时间 | NO |
| `watch_date` | DATE | 观看日期 | NO |
| `watch_hour` | INT | 观看小时 (0-23) | NO |
| `watch_dayofweek` | STRING | 星期几 | NO |
| `watch_month` | STRING | 观看月份 (YYYY-MM) | NO |
| `watch_year` | INT | 观看年份 | NO |
| `url` | STRING | 视频链接 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_source_file` | STRING | 原始文件名 | YES |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(watch_year, watch_month)`  
**Primary Key**: `video_id, watch_timestamp` (组合唯一)

---

#### silver_chrome_history

清洗后的浏览器历史。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `url` | STRING | 页面URL | NO |
| `domain` | STRING | 域名 (提取) | NO |
| `title` | STRING | 页面标题 | YES |
| `visit_time` | TIMESTAMP | 访问时间 | NO |
| `visit_date` | DATE | 访问日期 | NO |
| `visit_hour` | INT | 访问小时 | NO |
| `visit_dayofweek` | STRING | 星期几 | NO |
| `visit_month` | STRING | 访问月份 | NO |
| `visit_year` | INT | 访问年份 | NO |
| `visit_count` | INT | 当日访问次数 | DEFAULT 1 |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_source_file` | STRING | 原始文件名 | YES |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(visit_year, visit_month)`

---

#### silver_github_events

清洗后的 GitHub 事件。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `event_id` | STRING | 事件ID | NO |
| `event_type` | STRING | 事件类型 | NO |
| `actor_login` | STRING | 触发者用户名 | NO |
| `actor_id` | BIGINT | 触发者ID | YES |
| `repo_name` | STRING | 仓库名 | NO |
| `repo_id` | BIGINT | 仓库ID | YES |
| `action` | STRING | 具体动作 | YES |
| `created_at` | TIMESTAMP | 事件时间 | NO |
| `created_date` | DATE | 事件日期 | NO |
| `created_hour` | INT | 事件小时 | NO |
| `payload_json` | STRING | 负载JSON (裁剪) | YES |
| `is_public` | BOOLEAN | 是否公开 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(year(created_at), month(created_at))`

---

#### silver_weibo_trending

清洗后的微博热搜。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `rank` | INT | 排名 | NO |
| `keyword` | STRING | 热词 | NO |
| `hot_level` | STRING | 热度级别 | YES |
| `hot_value` | BIGINT | 热度值 | NO |
| `keyword_length` | INT | 热词长度 | NO |
| `is_number` | BOOLEAN | 是否包含数字 | NO |
| `url` | STRING | 链接 | YES |
| `category` | STRING | 分类 | YES |
| `fetch_time` | TIMESTAMP | 抓取时间 | NO |
| `fetch_date` | DATE | 抓取日期 | NO |
| `fetch_hour` | INT | 抓取小时 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(year(fetch_time), month(fetch_time), day(fetch_time))`

---

#### silver_twitter_trending

清洗后的 Twitter 热搜。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `rank` | INT | 排名 | NO |
| `trend_name` | STRING | 热词 | NO |
| `has_hashtag` | BOOLEAN | 是否包含标签 | NO |
| `tweet_volume` | BIGINT | 推文数 | YES |
| `is_promoted` | BOOLEAN | 是否推广 | NO |
| `fetch_time` | TIMESTAMP | 抓取时间 | NO |
| `fetch_date` | DATE | 抓取日期 | NO |
| `fetch_hour` | INT | 抓取小时 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(year(fetch_time), month(fetch_time), day(fetch_time))`

---

#### silver_stock_quotations

清洗后的股票行情。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `symbol` | STRING | 股票代码 | NO |
| `name` | STRING | 股票名称 | NO |
| `market` | STRING | 市场 (CN/US) | NO |
| `price` | DOUBLE | 当前价格 | NO |
| `change_pct` | DOUBLE | 涨跌幅 | NO |
| `is_up` | BOOLEAN | 是否上涨 | NO |
| `volume` | BIGINT | 成交量 | YES |
| `amount` | DOUBLE | 成交额 | YES |
| `high` | DOUBLE | 最高价 | YES |
| `low` | DOUBLE | 最低价 | YES |
| `open` | DOUBLE | 开盘价 | YES |
| `pre_close` | DOUBLE | 昨收价 | YES |
| `trade_time` | TIMESTAMP | 交易时间 | NO |
| `trade_date` | DATE | 交易日 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(trade_date)`

---

#### silver_cctv_news

清洗后的新闻联播。

| Column | Type | Description | Nullable |
|--------|------|-------------|----------|
| `title` | STRING | 新闻标题 | NO |
| `title_length` | INT | 标题长度 | NO |
| `content` | STRING | 新闻内容 | YES |
| `content_length` | INT | 内容长度 | YES |
| `url` | STRING | 原文链接 | YES |
| `word_count` | INT | 字数 | YES |
| `publish_time` | TIMESTAMP | 发布时间 | NO |
| `publish_date` | DATE | 发布日期 | NO |
| `program` | STRING | 节目名称 | NO |
| `fetch_time` | TIMESTAMP | 抓取时间 | NO |
| `_ingest_time` | TIMESTAMP | 摄入时间 | NO |
| `_batch_id` | STRING | 批次ID | NO |

**Partition**: `(publish_date)`

---

### 3.3 GOLD LAYER (Aggregated Data)

#### gold_youtube_monthly_stats

YouTube 每月观看统计。

| Column | Type | Description |
|--------|------|-------------|
| `year_month` | STRING | 年月 (YYYY-MM) |
| `total_watches` | INT | 总观看次数 |
| `unique_videos` | INT | 独立视频数 |
| `unique_channels` | INT | 独立频道数 |
| `top_10_channels` | STRING (JSON) | TOP 10 频道 |
| `total_watch_minutes` | BIGINT | 总观看分钟数 |
| `avg_daily_watches` | DOUBLE | 日均观看次数 |
| `most_active_hour` | INT | 最活跃小时 |
| `most_active_day` | STRING | 最活跃星期 |
| `_computed_at` | TIMESTAMP | 计算时间 |
| `_date_range_start` | DATE | 统计开始日期 |
| `_date_range_end` | DATE | 统计结束日期 |

**Partition**: `(year_month)`  
**Refresh**: 每日

---

#### gold_chrome_monthly_stats

Chrome 每月浏览统计。

| Column | Type | Description |
|--------|------|-------------|
| `year_month` | STRING | 年月 |
| `total_visits` | BIGINT | 总访问次数 |
| `unique_domains` | INT | 独立域名数 |
| `top_20_domains` | STRING (JSON) | TOP 20 域名 |
| `top_10_categories` | STRING (JSON) | TOP 10 分类 |
| `avg_daily_visits` | DOUBLE | 日均访问次数 |
| `most_active_hour` | INT | 最活跃小时 |
| `most_active_day` | STRING | 最活跃星期 |
| `new_domains_this_month` | INT | 本月新域名 |
| `_computed_at` | TIMESTAMP | 计算时间 |

**Partition**: `(year_month)`

---

#### gold_github_monthly_stats

GitHub 每月贡献统计。

| Column | Type | Description |
|--------|------|-------------|
| `year_month` | STRING | 年月 |
| `total_events` | INT | 总事件数 |
| `total_commits` | INT | 总提交数 |
| `total_prs` | INT | 总PR数 |
| `total_issues` | INT | 总Issue数 |
| `total_stars` | INT | 总获星数 |
| `repos_contributed` | STRING (JSON) | 贡献的仓库列表 |
| `active_days` | INT | 活跃天数 |
| `streak_days` | INT | 连续活跃天数 |
| `most_active_hour` | INT | 最活跃小时 |
| `_computed_at` | TIMESTAMP | 计算时间 |

**Partition**: `(year_month)`

---

#### gold_social_trending_agg

社交媒体热搜聚合统计。

| Column | Type | Description |
|--------|------|-------------|
| `trend_date` | DATE | 日期 |
| `source` | STRING | 来源 (weibo/twitter) |
| `avg_rank` | DOUBLE | 平均排名 |
| `total_occurrences` | INT | 热词出现次数 |
| `top_10_trends` | STRING (JSON) | TOP 10 热词 |
| `new_trends` | INT | 新上榜单数 |
| `_computed_at` | TIMESTAMP | 计算时��� |

**Partition**: `(trend_date, source)`

---

#### gold_stock_portfolio_summary

自选股组合汇总。

| Column | Type | Description |
|--------|------|-------------|
| `calc_date` | DATE | 计算日期 |
| `symbol` | STRING | 股票代码 |
| `name` | STRING | 股票名称 |
| `latest_price` | DOUBLE | 最新价 |
| `daily_change_pct` | DOUBLE | 当日涨跌幅 |
| `weekly_change_pct` | DOUBLE | 周涨跌幅 |
| `monthly_change_pct` | DOUBLE | 月涨跌幅 |
| `holding_status` | STRING | 持仓状态 (hold/sell/buy) |
| `_computed_at` | TIMESTAMP | 计算时间 |

**Partition**: `(calc_date)`

---

#### gold_personal_dashboard

个人数据仪表盘汇总。

| Column | Type | Description |
|--------|------|-------------|
| `dashboard_date` | DATE | 日期 |
| `youtube_watches_mtd` | INT | YouTube 本月观看 |
| `github_commits_mtd` | INT | GitHub 本月提交 |
| `chrome_days_active` | INT | Chrome 活跃天数 |
| `top_weibo_trend` | STRING | 微博热搜第一 |
| `portfolio_value` | DOUBLE | 组合市值 |
| `portfolio_change` | DOUBLE | 组合涨跌 |
| `news_count_today` | INT | 今日新闻数 |
| `_computed_at` | TIMESTAMP | 计算时间 |

**Partition**: `(dashboard_date)`

---

## 4. DATA FLOW SUMMARY

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  RAW SOURCES      BRONZE (Raw)         SILVER (Cleaned)    GOLD (Agg)     │
│  ──────────       ─────────────        ───────────────     ──────────     │
│                                                                             │
│  Takeout JSON  ──▶ bronze_youtube    ──▶ silver_youtube   ──▶ gold_*     │
│  Chrome JSON  ──▶ bronze_chrome      ──▶ silver_chrome    ──▶ gold_*     │
│  Webhook      ──▶ bronze_github      ──▶ silver_github    ──▶ gold_*     │
│  API          ──▶ bronze_weibo       ──▶ silver_weibo     ──▶ gold_*     │
│  API          ──▶ bronze_twitter     ──▶ silver_twitter   ──▶ gold_*     │
│  akshare     ──▶ bronze_stock       ──▶ silver_stock     ──▶ gold_*     │
│  爬虫         ──▶ bronze_cctv_news  ──▶ silver_cctv_news  ──▶ gold_*     │
│  爬虫         ──▶ bronze_github_    ──▶ silver_github_   ──▶ gold_*     │
│                              trending    trending             trending     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. RETENTION POLICY

| Layer | Retention | Justification |
|-------|-----------|---------------|
| Bronze | 永久 | 保留原始数据用于重新处理 |
| Silver | 3年 | 清洗后数据保留3年 |
| Gold | 永久 | 聚合指标是核心资产 |

---

*Generated: 2025-06-07*