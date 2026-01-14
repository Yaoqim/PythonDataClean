# -*- coding: utf-8 -*-
"""
数据库结构更新脚本 (迁移脚本)
用于在不删除现有数据的情况下，增加 missing 的字段和表，并添加中文注释。
"""
import sys
from pathlib import Path

# 将项目根目录添加到 python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db_service.db_manager import DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

def migrate():
    db = DatabaseManager()
    
    # 1. 重建 processed_files 表 (如果结构不一致)
    logger.info("正在更新 processed_files 表...")
    db.execute_sql("DROP TABLE IF EXISTS processed_files;")
    db.execute_sql("""
    CREATE TABLE processed_files (
      `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
      `file_hash` VARCHAR(64) NOT NULL UNIQUE COMMENT '文件MD5哈希值，用于防重校验',
      `file_path` VARCHAR(500) NOT NULL COMMENT '原始文件路径 (OSS路径或本地路径)',
      `business_type` VARCHAR(50) COMMENT '业务类型标识 (如 CUSTOMER_DIALOG)',
      `process_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '处理完成时间',
      `status` VARCHAR(20) DEFAULT 'success' COMMENT '处理状态 (success/failed/processing)',
      `row_count` INT DEFAULT 0 COMMENT '该文件成功处理的数据行数',
      KEY idx_file_hash (file_hash)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='已处理文件记录表(防重与溯源基础)';
    """)

    # 2. 为电商商品信息表增加 source_file
    logger.info("正在为 ec_product_info 增加 source_file 字段...")
    try:
        db.execute_sql("ALTER TABLE ec_product_info ADD COLUMN `source_file` VARCHAR(500) COMMENT '原始数据来源文件路径 (用于数据溯源)' AFTER `clean_time`;")
    except Exception as e:
        logger.warning(f"ec_product_info source_file 可能已存在: {e}")

    # 3. 为电商商品评论表增加 source_file
    logger.info("正在为 ec_comment_2024 增加 source_file 字段...")
    try:
        db.execute_sql("ALTER TABLE ec_comment_2024 ADD COLUMN `source_file` VARCHAR(500) COMMENT '原始数据来源文件路径 (用于数据溯源)' AFTER `comment_id_anal_info`;")
    except Exception as e:
        logger.warning(f"ec_comment_2024 source_file 可能已存在: {e}")

    # 4. 为客户对话表增加 order_id 和 source_file
    logger.info("正在为 customer_conversation 增加字段...")
    try:
        db.execute_sql("ALTER TABLE customer_conversation ADD COLUMN `order_id` VARCHAR(100) COMMENT '关联订单号 (用于身份识别辅助)' AFTER `agent_name_anal_info`;")
    except Exception as e:
        logger.warning(f"customer_conversation order_id 可能已存在: {e}")
    
    try:
        db.execute_sql("ALTER TABLE customer_conversation ADD COLUMN `source_file` VARCHAR(500) COMMENT '原始数据来源文件路径 (用于数据溯源)' AFTER `order_id`;")
    except Exception as e:
        logger.warning(f"customer_conversation source_file 可能已存在: {e}")

    logger.info("数据库迁移完成！")

if __name__ == "__main__":
    migrate()
