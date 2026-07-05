"""
Great Expectations Data Quality Suites for Personal Data Lakehouse
"""

# ============================================================
# BRONZE LAYER - Expectation Suites
# ============================================================

BRONZE_YOUTUBE_WATCHES_SUITE = {
    "name": "bronze_youtube_watches",
    "meta": {
        "description": "YouTube watch history raw data validation",
        "layer": "bronze",
        "source": "google_takeout"
    },
    "expectations": [
        {
            "expectation_type": "expect_table_columns_to_match_ordered_list",
            "kwargs": {
                "column_list": [
                    "header", "title", "titleUrl", "time",
                    "subtitles", "details", "imports",
                    "_raw_json", "_ingest_time", "_batch_id", "_source_file"
                ]
            }
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {
                "column": "title",
                "mostly": 0.95
            }
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {
                "column": "time",
                "mostly": 0.95
            }
        },
        {
            "expectation_type": "expect_column_values_to_match_regex",
            "kwargs": {
                "column": "titleUrl",
                "regex": "^https?://.*",
                "mostly": 0.9
            }
        },
        {
            "expectation_type": "expect_column_values_to_be_of_type",
            "kwargs": {
                "column": "_ingest_time",
                "type_": "TimestampType"
            }
        }
    ]
}

BRONZE_CHROME_HISTORY_SUITE = {
    "name": "bronze_chrome_history",
    "meta": {
        "description": "Chrome browser history raw data validation",
        "layer": "bronze",
        "source": "google_takeout"
    },
    "expectations": [
        {
            "expectation_type": "expect_table_columns_to_match_ordered_list",
            "kwargs": {
                "column_list": [
                    "browser_name", "datetime", "url", "title",
                    "visits", "_raw_json", "_ingest_time", "_batch_id", "_source_file"
                ]
            }
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "url", "mostly": 0.99}
        },
        {
            "expectation_type": "expect_column_values_to_match_regex",
            "kwargs": {
                "column": "url",
                "regex": "^https?://.*",
                "mostly": 0.95
            }
        },
        {
            "expectation_type": "expect_column_values_to_be_of_type",
            "kwargs": {"column": "_ingest_time", "type_": "TimestampType"}
        }
    ]
}

BRONE_GITHUB_EVENTS_SUITE = {
    "name": "bronze_github_events",
    "meta": {
        "description": "GitHub events raw data validation",
        "layer": "bronze",
        "source": "github_webhook"
    },
    "expectations": [
        {
            "expectation_type": "expect_table_columns_to_match_ordered_list",
            "kwargs": {
                "column_list": [
                    "event_id", "event_type", "actor", "repo", "payload",
                    "public_flag", "created_at", "_raw_json",
                    "_ingest_time", "_batch_id", "_source"
                ]
            }
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "event_id"}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "event_type"}
        },
        {
            "expectation_type": "expect_column_values_to_be_in_set",
            "kwargs": {
                "column": "event_type",
                "value_set": [
                    "PushEvent", "PullRequestEvent", "IssuesEvent",
                    "WatchEvent", "CreateEvent", "DeleteEvent",
                    "ForkEvent", "IssueCommentEvent", "PullRequestReviewEvent"
                ]
            }
        }
    ]
}

# ============================================================
# SILVER LAYER - Expectation Suites
# ============================================================

SILVER_YOUTUBE_WATCHES_SUITE = {
    "name": "silver_youtube_watches",
    "meta": {
        "description": "YouTube watch history cleaned data validation",
        "layer": "silver",
        "source": "youtube",
        "dq_level": "strict"
    },
    "expectations": [
        # Schema validation
        {
            "expectation_type": "expect_table_columns_to_match_ordered_list",
            "kwargs": {
                "column_list": [
                    "video_id", "video_title", "channel_id", "channel_name",
                    "watch_timestamp", "watch_date", "watch_hour", "watch_dayofweek",
                    "watch_month", "watch_year", "url",
                    "_ingest_time", "_source_file", "_batch_id"
                ]
            }
        },
        # Not null constraints
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "video_id", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "video_title", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "watch_timestamp", "mostly": 1.0}
        },
        # Uniqueness
        {
            "expectation_type": "expect_column_values_to_be_unique",
            "kwargs": {"column": "video_id", "mostly": 0.8}
        },
        # Data type validation
        {
            "expectation_type": "expect_column_values_to_be_of_type",
            "kwargs": {"column": "watch_timestamp", "type_": "TimestampType"}
        },
        {
            "expectation_type": "expect_column_values_to_be_of_type",
            "kwargs": {"column": "watch_date", "type_": "DateType"}
        },
        # Range validation
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "watch_hour",
                "min_value": 0,
                "max_value": 23
            }
        },
        {
            "expectation_type": "expect_column_values_to_be_in_set",
            "kwargs": {
                "column": "watch_dayofweek",
                "value_set": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            }
        },
        # Freshness
        {
            "expectation_type": "expect_column_values_to_be_after",
            "kwargs": {
                "column": "watch_timestamp",
                "max_value": "2025-12-31",
                "mostly": 1.0
            }
        }
    ]
}

SILVER_CHROME_HISTORY_SUITE = {
    "name": "silver_chrome_history",
    "meta": {
        "description": "Chrome history cleaned data validation",
        "layer": "silver",
        "source": "chrome",
        "dq_level": "strict"
    },
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "url", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "domain", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "visit_time", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_match_regex",
            "kwargs": {"column": "url", "regex": r"^https?://", "mostly": 0.95}
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {"column": "visit_hour", "min_value": 0, "max_value": 23}
        }
    ]
}

SILVER_GITHUB_EVENTS_SUITE = {
    "name": "silver_github_events",
    "meta": {
        "description": "GitHub events cleaned data validation",
        "layer": "silver",
        "source": "github",
        "dq_level": "strict"
    },
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "event_id"}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "event_type"}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "actor_login"}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "repo_name"}
        },
        {
            "expectation_type": "expect_column_values_to_be_in_set",
            "kwargs": {
                "column": "event_type",
                "value_set": [
                    "PushEvent", "PullRequestEvent", "IssuesEvent",
                    "WatchEvent", "CreateEvent", "DeleteEvent",
                    "ForkEvent", "IssueCommentEvent", "PullRequestReviewEvent",
                    "ReleaseEvent", "PullRequestReviewCommentEvent"
                ]
            }
        }
    ]
}

SILVER_STOCK_QUOTATIONS_SUITE = {
    "name": "silver_stock_quotations",
    "meta": {
        "description": "Stock quotations cleaned data validation",
        "layer": "silver",
        "source": "stock",
        "dq_level": "strict"
    },
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "symbol", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "price", "mostly": 1.0}
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {"column": "price", "min_value": 0, "max_value": 1000000}
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {"column": "change_pct", "min_value": -100, "max_value": 100}
        },
        {
            "expectation_type": "expect_column_values_to_be_in_set",
            "kwargs": {"column": "market", "value_set": ["CN", "US"]}
        }
    ]
}

# ============================================================
# GOLD LAYER - Expectation Suites
# ============================================================

GOLD_YOUTUBE_MONTHLY_STATS_SUITE = {
    "name": "gold_youtube_monthly_stats",
    "meta": {
        "description": "YouTube monthly aggregation validation",
        "layer": "gold",
        "source": "youtube",
        "dq_level": "critical"
    },
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "year_month"}
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "total_watches",
                "min_value": 0
            }
        },
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "unique_videos",
                "min_value": 0
            }
        },
        {
            "expectation_type": "expect_column_values_to_match_regex",
            "kwargs": {
                "column": "year_month",
                "regex": r"^\d{4}-(0[1-9]|1[0-2])$"
            }
        },
        # Sanity check: unique videos <= total watches
        {
            "expectation_type": "expect_column_pair_values_to_be_equal",
            "kwargs": {
                "column_A": "unique_videos",
                "column_B": "total_watches",
                "row_condition": "unique_videos <= total_watches",
                "condition_parser": "pandas"
            }
        }
    ]
}

# ============================================================
# Cross-Layer Validation
# ============================================================

DATA_FRESHNESS_CHECKS = {
    "name": "data_freshness_checks",
    "description": "Verify data is up-to-date",
    "checks": [
        {
            "name": "silver_youtube_freshness",
            "table": "lakehouse.silver_youtube_watches",
            "max_age_hours": 168,  # 7 days for weekly batch
            "timestamp_column": "_ingest_time"
        },
        {
            "name": "silver_github_freshness",
            "table": "lakehouse.silver_github_events",
            "max_age_hours": 24,  # 1 day
            "timestamp_column": "_ingest_time"
        },
        {
            "name": "silver_stock_freshness",
            "table": "lakehouse.silver_stock_quotations",
            "max_age_hours": 1,  # 1 hour for stock
            "timestamp_column": "_ingest_time"
        }
    ]
}

# ============================================================
# DQ Alert Configuration
# ============================================================

DQ_ALERT_CONFIG = {
    "channels": [
        {
            "type": "log",
            "level": "ERROR",
            "destination": "lakehouse.dq_check_results"
        },
        {
            "type": "console",
            "level": "WARNING"
        }
    ],
    "rules": [
        {
            "severity": "critical",
            "condition": "failure_percentage > 5",
            "action": "block_pipeline"
        },
        {
            "severity": "warning",
            "condition": "failure_percentage > 1",
            "action": "notify"
        },
        {
            "severity": "info",
            "condition": "failure_percentage > 0",
            "action": "log"
        }
    ]
}