# -*- coding: utf-8 -*-
"""检查环境变量是否加载"""

import os
from pathlib import Path

# 主动加载 .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
        print(f"\n✔ 已加载 .env 文件")
except ImportError:
    pass

print("\n环境变量检查")
print("="*80)

print(f"\n1. .env 文件路径:")
env_path = Path(__file__).parent / '.env'
print(f"   {env_path}")
print(f"   存在：{env_path.exists()}")

print(f"\n2. OSS相关环境变量:")
print(f"   OSS_ACCESS_KEY_ID: {os.getenv('OSS_ACCESS_KEY_ID', 'NOT SET')}")
print(f"   OSS_ACCESS_KEY_SECRET: {os.getenv('OSS_ACCESS_KEY_SECRET', 'NOT SET')}")
print(f"   RUN_MODE: {os.getenv('RUN_MODE', 'NOT SET')}")
print(f"   DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")

print("\n3. .env文件内容（前几行）:")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:10]
        for line in lines:
            print(f"   {line.rstrip()}")
