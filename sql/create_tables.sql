-- ============================================================
-- Personal Data Lakehouse: Table Creation Scripts
-- Target: Iceberg on MinIO via Gravitino/Trino
-- ============================================================

-- ============================================================
-- BRONZE LAYER (Raw Data)
-- ============================================================

-- Bronze: YouTube Watch History
CREATE TABLE IF NOT EXISTS lakehouse.bronze_youtube_watches (
    header STRING,
    title STRING,
    titleUrl STRING,
    time STRING,
    subtitles STRING,
    details STRING,
    imports STRING,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING,
    _source_file STRING
)
USING iceberg
PARTITIONED BY (years(_ingest_time))
TBLPROPERTIES (
    'format-version' = '2',
    'write.distribution-mode' = 'hash'
);

-- Bronze: Chrome History
CREATE TABLE IF NOT EXISTS lakehouse.bronze_chrome_history (
    browser_name STRING,
    datetime STRING,
    url STRING,
    title STRING,
    visits STRING,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING,
    _source_file STRING
)
USING iceberg
PARTITIONED BY (years(_ingest_time));

-- Bronze: GitHub Events
CREATE TABLE IF NOT EXISTS lakehouse.bronze_github_events (
    event_id STRING,
    event_type STRING,
    actor STRING,
    repo STRING,
    payload STRING,
    public_flag BOOLEAN,
    created_at STRING,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING,
    _source STRING
)
USING iceberg
PARTITIONED BY (months(_ingest_time));

-- Bronze: Weibo Trending
CREATE TABLE IF NOT EXISTS lakehouse.bronze_weibo_trending (
    rank_value INT,
    keyword STRING,
    hot_level STRING,
    hot_value BIGINT,
    url STRING,
    category STRING,
    fetch_time TIMESTAMP,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (hours(fetch_time));

-- Bronze: Twitter Trending
CREATE TABLE IF NOT EXISTS lakehouse.bronze_twitter_trending (
    rank_value INT,
    trend_name STRING,
    tweet_volume BIGINT,
    fetch_time TIMESTAMP,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (hours(fetch_time));

-- Bronze: Stock Quotations
CREATE TABLE IF NOT EXISTS lakehouse.bronze_stock_quotations (
    symbol STRING,
    name STRING,
    market STRING,
    price DOUBLE,
    change_pct DOUBLE,
    volume BIGINT,
    amount DOUBLE,
    high DOUBLE,
    low DOUBLE,
    open_price DOUBLE,
    pre_close DOUBLE,
    trade_time TIMESTAMP,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (days(trade_time));

-- Bronze: CCTV News
CREATE TABLE IF NOT EXISTS lakehouse.bronze_cctv_news (
    title STRING,
    content STRING,
    url STRING,
    publish_time TIMESTAMP,
    program STRING,
    fetch_time TIMESTAMP,
    _raw_html STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (days(publish_time));

-- Bronze: GitHub Trending
CREATE TABLE IF NOT EXISTS lakehouse.bronze_github_trending (
    repo_name STRING,
    description STRING,
    language STRING,
    stars INT,
    forks INT,
    today_stars INT,
    contributors INT,
    url STRING,
    fetch_date DATE,
    created_at TIMESTAMP,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (days(fetch_date));

-- Bronze: Bilibili Trending
CREATE TABLE IF NOT EXISTS lakehouse.bronze_bilibili_trending (
    rank_value INT,
    title STRING,
    description STRING,
    url STRING,
    bvid STRING,
    author STRING,
    view_count BIGINT,
    like_count BIGINT,
    reply_count BIGINT,
    category STRING,
    fetch_time TIMESTAMP,
    _raw_json STRING,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (hours(fetch_time));



-- ============================================================
-- SILVER LAYER (Cleaned Data)
-- ============================================================

-- Silver: YouTube Watches (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_youtube_watches (
    video_id STRING,
    video_title STRING,
    channel_id STRING,
    channel_name STRING,
    watch_timestamp TIMESTAMP,
    watch_date DATE,
    watch_hour INT,
    watch_dayofweek STRING,
    watch_month STRING,
    watch_year INT,
    url STRING,
    _ingest_time TIMESTAMP,
    _source_file STRING,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(watch_timestamp), months(watch_timestamp))
TBLPROPERTIES (
    'format-version' = '2',
    'write.distribution-mode' = 'hash',
    'write.metadata.delete-after-commit.enabled' = 'true'
);

-- Silver: Chrome History (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_chrome_history (
    url STRING,
    domain STRING,
    title STRING,
    visit_time TIMESTAMP,
    visit_date DATE,
    visit_hour INT,
    visit_dayofweek STRING,
    visit_month STRING,
    visit_year INT,
    visit_count INT,
    _ingest_time TIMESTAMP,
    _source_file STRING,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(visit_time), months(visit_time));

-- Silver: GitHub Events (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_github_events (
    event_id STRING,
    event_type STRING,
    actor_login STRING,
    actor_id BIGINT,
    repo_name STRING,
    repo_id BIGINT,
    action STRING,
    created_at TIMESTAMP,
    created_date DATE,
    created_hour INT,
    payload_json STRING,
    is_public BOOLEAN,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(created_at), months(created_at));

-- Silver: Weibo Trending (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_weibo_trending (
    rank_value INT,
    keyword STRING,
    hot_level STRING,
    hot_value BIGINT,
    keyword_length INT,
    is_number BOOLEAN,
    url STRING,
    category STRING,
    fetch_time TIMESTAMP,
    fetch_date DATE,
    fetch_hour INT,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(fetch_time), months(fetch_time), days(fetch_time));

-- Silver: Twitter Trending (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_twitter_trending (
    rank_value INT,
    trend_name STRING,
    has_hashtag BOOLEAN,
    tweet_volume BIGINT,
    is_promoted BOOLEAN,
    fetch_time TIMESTAMP,
    fetch_date DATE,
    fetch_hour INT,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(fetch_time), months(fetch_time), days(fetch_time));

-- Silver: GitHub Trending (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_github_trending (
    rank_value INT,
    repo_name STRING,
    repo_owner STRING,
    repo_name_only STRING,
    description STRING,
    description_length INT,
    language STRING,
    stars INT,
    forks INT,
    today_stars INT,
    contributors INT,
    url STRING,
    fetch_date DATE,
    created_at TIMESTAMP,
    is_starred_above_100k BOOLEAN,
    is_starred_above_50k BOOLEAN,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(fetch_date), months(fetch_date));

-- Silver: Bilibili Trending (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_bilibili_trending (
    rank_value INT,
    title STRING,
    title_length INT,
    has_description BOOLEAN,
    description STRING,
    url STRING,
    bvid STRING,
    author STRING,
    view_count BIGINT,
    like_count BIGINT,
    reply_count BIGINT,
    comment_rate DOUBLE,
    category STRING,
    fetch_time TIMESTAMP,
    fetch_date DATE,
    fetch_hour INT,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (years(fetch_time), months(fetch_time), days(fetch_time));

-- Silver: Stock Quotations (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_stock_quotations (
    symbol STRING NOT NULL,
    name STRING,
    market STRING NOT NULL,
    price DOUBLE NOT NULL,
    change_pct DOUBLE NOT NULL,
    is_up BOOLEAN,
    volume BIGINT,
    amount DOUBLE,
    high DOUBLE,
    low DOUBLE,
    open_price DOUBLE,
    pre_close DOUBLE,
    trade_time TIMESTAMP NOT NULL,
    trade_date DATE,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (days(trade_date));

-- Silver: CCTV News (Cleaned)
CREATE TABLE IF NOT EXISTS lakehouse.silver_cctv_news (
    title STRING NOT NULL,
    title_length INT,
    content STRING,
    content_length INT,
    url STRING,
    word_count INT,
    publish_time TIMESTAMP NOT NULL,
    publish_date DATE,
    program STRING,
    fetch_time TIMESTAMP,
    _ingest_time TIMESTAMP,
    _batch_id STRING
)
USING iceberg
PARTITIONED BY (days(publish_date));



-- ============================================================
-- GOLD LAYER (Aggregated)
-- ============================================================

-- Gold: YouTube Monthly Stats
CREATE TABLE IF NOT EXISTS lakehouse.gold_youtube_monthly_stats (
    year_month STRING,
    total_watches INT,
    unique_videos INT,
    unique_channels INT,
    top_10_channels STRING,  -- JSON array
    total_watch_minutes BIGINT,
    avg_daily_watches DOUBLE,
    most_active_hour INT,
    most_active_day STRING,
    _computed_at TIMESTAMP,
    _date_range_start DATE,
    _date_range_end DATE
)
USING iceberg
PARTITIONED BY (years(_computed_at), months(_computed_at));

-- Gold: Chrome Monthly Stats
CREATE TABLE IF NOT EXISTS lakehouse.gold_chrome_monthly_stats (
    year_month STRING,
    total_visits BIGINT,
    unique_domains INT,
    top_20_domains STRING,  -- JSON array
    top_10_categories STRING,
    avg_daily_visits DOUBLE,
    most_active_hour INT,
    most_active_day STRING,
    new_domains_this_month INT,
    _computed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (years(_computed_at), months(_computed_at));

-- Gold: GitHub Monthly Stats
CREATE TABLE IF NOT EXISTS lakehouse.gold_github_monthly_stats (
    year_month STRING,
    total_events INT,
    total_commits INT,
    total_prs INT,
    total_issues INT,
    total_stars INT,
    repos_contributed STRING,  -- JSON array
    active_days INT,
    streak_days INT,
    most_active_hour INT,
    _computed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (years(_computed_at), months(_computed_at));

-- Gold: Social Trending Aggregate
CREATE TABLE IF NOT EXISTS lakehouse.gold_social_trending_agg (
    trend_date DATE,
    source STRING,
    avg_rank DOUBLE,
    total_occurrences INT,
    top_10_trends STRING,
    new_trends INT,
    _computed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (years(trend_date));

-- Gold: Stock Portfolio Summary
CREATE TABLE IF NOT EXISTS lakehouse.gold_stock_portfolio_summary (
    calc_date DATE,
    symbol STRING NOT NULL,
    name STRING,
    latest_price DOUBLE,
    daily_change_pct DOUBLE,
    weekly_change_pct DOUBLE,
    monthly_change_pct DOUBLE,
    holding_status STRING,
    _computed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(calc_date));

-- Gold: Personal Dashboard
CREATE TABLE IF NOT EXISTS lakehouse.gold_personal_dashboard (
    dashboard_date DATE,
    youtube_watches_mtd INT,
    github_commits_mtd INT,
    chrome_days_active INT,
    top_weibo_trend STRING,
    portfolio_value DOUBLE,
    portfolio_change DOUBLE,
    news_count_today INT,
    _computed_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(dashboard_date));



-- ============================================================
-- AUDIT LOG TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS lakehouse.audit_logs (
    timestamp TIMESTAMP,
    user_id STRING,
    api_key_id STRING,
    action STRING,
    resource_type STRING,
    resource_name STRING,
    details STRING,
    status STRING,
    client_ip STRING
)
USING iceberg
PARTITIONED BY (days(timestamp));



-- ============================================================
-- DATA QUALITY CHECK RESULTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS lakehouse.dq_check_results (
    check_id STRING,
    check_name STRING,
    table_name STRING,
    column_name STRING,
    check_type STRING,
    check_result STRING,  -- PASS/FAIL
    expected_value STRING,
    actual_value STRING,
    failure_count BIGINT,
    failure_percentage DOUBLE,
    checked_at TIMESTAMP,
    batch_id STRING
)
USING iceberg
PARTITIONED BY (years(checked_at), months(checked_at));