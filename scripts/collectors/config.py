#!/usr/bin/env python3
"""
配置加载模块
Security: 从环境变量加载敏感配置
"""

import os
from pathlib import Path

# 配置目录
CONFIG_DIR = Path.home() / ".config" / "lakehouse"
ENV_FILE = Path.home() / ".lakehouse_env"


def load_env():
    """加载环境变量配置"""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())


def get_github_token() -> str:
    """获取 GitHub Token"""
    load_env()
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("Warning: GITHUB_TOKEN not found. Set in ~/.lakehouse_env")
    return token


def get_config(key: str, default=None):
    """获取配置项"""
    load_env()
    return os.environ.get(key, default)


# 测试
if __name__ == "__main__":
    print("Testing config loading...")
    token = get_github_token()
    print(f"GitHub Token: {token[:20]}..." if token else "Not found")