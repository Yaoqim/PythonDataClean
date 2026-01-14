# -*- coding: utf-8 -*-
"""
数据导入脚本：将清洗后的客户对话数据导入数据库
"""

import json
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from config.db_credentials import DatabaseCredentials

logger = get_logger(__name__)

def import_cleaned_data(file_path):
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        if not records:
            logger.warning("没有可导入的数据")
            return True

        # 获取数据库连接
        credentials = DatabaseCredentials()
        engine = create_engine(credentials.get_connection_string())

        insert_sql = """
        INSERT INTO customer_conversation (
            knowledge_id, conversation_id, user_id, merchant_name, merchant_name_anal, merchant_name_anal_info,
            customer_name, customer_name_anal, customer_name_anal_info,
            agent_name, agent_name_anal, agent_name_anal_info,
            product_name, message_type, message_type_anal, message_type_anal_info,
            message_content, message_content_anal, message_content_anal_info,
            message_time, message_time_anal, message_time_anal_info,
            platform, platform_anal, platform_anal_info,
            sentiment, conversation_status, resolution_time, satisfaction,
            data_crawl_date, data_update_time, cleaned_at, is_valid, validity_reason,
            quality_score, data_status, version
        ) VALUES (
            :knowledge_id, :conversation_id, :user_id, :merchant_name, :merchant_name_anal, :merchant_name_anal_info,
            :customer_name, :customer_name_anal, :customer_name_anal_info,
            :agent_name, :agent_name_anal, :agent_name_anal_info,
            :product_name, :message_type, :message_type_anal, :message_type_anal_info,
            :message_content, :message_content_anal, :message_content_anal_info,
            :message_time, :message_time_anal, :message_time_anal_info,
            :platform, :platform_anal, :platform_anal_info,
            :sentiment, :conversation_status, :resolution_time, :satisfaction,
            :data_crawl_date, :data_update_time, :cleaned_at, :is_valid, :validity_reason,
            :quality_score, :data_status, :version
        ) ON DUPLICATE KEY UPDATE
            conversation_id = VALUES(conversation_id),
            user_id = VALUES(user_id),
            merchant_name = VALUES(merchant_name),
            quality_score = VALUES(quality_score),
            data_status = VALUES(data_status),
            last_updated_at = CURRENT_TIMESTAMP
        """

        with engine.begin() as conn:
            # 批量执行
            conn.execute(text(insert_sql), records)
            
        logger.info(f"成功导入 {len(records)} 条记录到 customer_conversation 表")
        return True

    except Exception as e:
        logger.error(f"导入数据失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    cleaned_file = "data/processed/CUSTOMER_DIALOG_CLEANED.json"
    success = import_cleaned_data(cleaned_file)
    sys.exit(0 if success else 1)
