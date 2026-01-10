# -*- coding: utf-8 -*-
"""检查OSS中是否存在文件"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
env_path = Path('.env')
if env_path.exists():
    load_dotenv(dotenv_path=str(env_path), override=False)

# 检查环境变量
print('OSS凭证检查：')
print(f'  • OSS_ACCESS_KEY_ID: {"已设置" if os.getenv("OSS_ACCESS_KEY_ID") else "未设置"}')
print(f'  • OSS_ACCESS_KEY_SECRET: {"已设置" if os.getenv("OSS_ACCESS_KEY_SECRET") else "未设置"}')

# 尝试连接OSS并列表文件
try:
    import oss2
    auth = oss2.Auth(os.getenv('OSS_ACCESS_KEY_ID'), os.getenv('OSS_ACCESS_KEY_SECRET'))
    bucket = oss2.Bucket(auth, 'oss-cn-beijing.aliyuncs.com', 'letwx')
    
    print('\nOSS中的文件列表：')
    files = list(oss2.ObjectIterator(bucket, prefix='ai_network_data'))
    if files:
        for obj in files[:20]:  # 只显示前20个
            print(f'  • {obj.key}')
    else:
        print('  • 找不到ai_network_data前缀的文件')
        
    print(f'\n总共找到 {len(files)} 个文件')
    
    # 检查特定文件
    specific_file = 'ai_network_data/EC_GOODS_PHONE_20260109_0001.json'
    print(f'\n检查特定文件：{specific_file}')
    exists = bucket.object_exists(specific_file)
    print(f'  • 文件存在：{exists}')
    
except Exception as e:
    print(f'连接OSS失败：{e}')
    import traceback
    traceback.print_exc()
