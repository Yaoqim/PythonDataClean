# -*- coding: utf-8 -*-
"""调试OSS路径检查"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=False)

from src.file_service.aliyun_client import AliyunOSSClient
from config import yaml_loader

print("\n" + "="*80)
print("OSS配置和路径调试")
print("="*80)

# 获取配置信息
aliyun_config = yaml_loader.get('aliyun', {})
oss_config = aliyun_config.get('oss', {})

print("\n【YAML配置信息】")
print(f"  • Endpoint: {oss_config.get('endpoint')}")
print(f"  • BucketName: {oss_config.get('bucketName')}")
print(f"  • OSS_ACCESS_KEY_ID: {'已设置' if os.getenv('OSS_ACCESS_KEY_ID') else '未设置'}")
print(f"  • OSS_ACCESS_KEY_SECRET: {'已设置' if os.getenv('OSS_ACCESS_KEY_SECRET') else '未设置'}")

# 初始化OSS客户端
print("\n【初始化OSS客户端】")
oss_client = AliyunOSSClient()
print(f"  • 连接状态: {oss_client.is_connected()}")
print(f"  • Endpoint: {oss_client.endpoint}")
print(f"  • BucketName: {oss_client.bucket_name}")

# 测试路径规范化
test_paths = [
    "oss://letwx/ai_network_data/EC_GOODS_PHONE_20260109_0001.json",
    "/ai_network_data/EC_GOODS_PHONE_20260109_0001.json",
    "ai_network_data/EC_GOODS_PHONE_20260109_0001.json"
]

print("\n【路径规范化测试】")
for path in test_paths:
    if path.startswith('oss://'):
        oss_path = '/' + path.split('/', 3)[-1]
    else:
        oss_path = path
    print(f"  • 原始: {path}")
    print(f"    → 规范化: {oss_path}")
    
    if oss_client.is_connected():
        exists = oss_client.file_exists(oss_path)
        print(f"    → 文件存在: {exists}")
    print()

# 列出OSS中的文件
print("\n【列出OSS中的文件】")
if oss_client.is_connected():
    files = oss_client.list_files(prefix='ai_network_data')
    if files:
        print(f"  找到 {len(files)} 个文件：")
        for f in files[:10]:
            print(f"    • {f}")
        if len(files) > 10:
            print(f"    ... 还有 {len(files)-10} 个文件")
    else:
        print("  • 没有找到以 'ai_network_data' 开头的文件")
        
    # 尝试列出根目录文件
    print("\n【尝试列出OSS根目录文件】")
    all_files = oss_client.list_files(prefix='')
    print(f"  • OSS中总共有 {len(all_files)} 个文件")
    if all_files:
        print("  前20个文件：")
        for f in all_files[:20]:
            print(f"    • {f}")

print("\n" + "="*80)
