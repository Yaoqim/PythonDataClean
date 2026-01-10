# -*- coding: utf-8 -*-
"""
重新初始化数据库 - 先删除旧表再创建新表
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from config.db_credentials import DatabaseCredentials
from sqlalchemy import create_engine, text, inspect

logger = get_logger(__name__)

# 要删除的旧表列表
TABLES_TO_DROP = ['ec_product_info_tag', 'ec_product_info']

def drop_tables():
    """删除旧表"""
    try:
        credentials = DatabaseCredentials()
        connection_string = credentials.get_connection_string()
        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            # 先关闭外键检查
            connection.execute(text('SET FOREIGN_KEY_CHECKS=0'))
            
            for table_name in TABLES_TO_DROP:
                try:
                    connection.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
                    logger.info(f"表已删除: {table_name}")
                except Exception as e:
                    logger.warning(f"删除表失败: {table_name}: {e}")
            
            # 恢复外键检查
            connection.execute(text('SET FOREIGN_KEY_CHECKS=1'))
            connection.commit()
            
        logger.info("旧表删除完成")
        return True
        
    except Exception as e:
        logger.error(f"删除表失败: {e}")
        return False


if __name__ == '__main__':
    # 删除旧表
    success = drop_tables()
    
    if success:
        print("\n[OK] 旧表已删除，请运行 python scripts/init_db.py 重新创建表")
    else:
        print("\n[ERROR] 删除失败")
        sys.exit(1)

