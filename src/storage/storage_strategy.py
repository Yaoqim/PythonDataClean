# -*- coding: utf-8 -*-
"""
存储策略

负责将清洗后的数据按业务规则存入数据库表。
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.db_service.db_manager import get_database_manager
from src.metadata.business_type_registry import BusinessTypeRegistry

logger = get_logger(__name__)


class StorageStrategy:
    """存储策略"""
    
    @staticmethod
    def store_records(
        business_type_id: str,
        records: List[Dict[str, Any]]
    ) -> Tuple[int, int, str]:
        """
        存储清洗后的记录到数据库
        
        Args:
            business_type_id: 业务类型ID
            records: 清洗后的记录列表
        
        Returns:
            (成功数, 失败数, 目标表名)
        """
        if not records:
            logger.warning(f"没有要存储的记录：{business_type_id}")
            return 0, 0, ""
        
        # 获取业务类型配置
        config = BusinessTypeRegistry.get(business_type_id)
        if not config:
            logger.error(f"业务类型不支持：{business_type_id}")
            return 0, len(records), ""
        
        table_name = config.get('table_name')
        if not table_name:
            logger.error(f"未配置表名：{business_type_id}")
            return 0, len(records), ""
        
        # 添加时间戳
        for record in records:
            record['clean_time'] = datetime.now().isoformat()
        
        try:
            # 调用数据库管理器批量插入
            db_manager = get_database_manager()
            success, failed = db_manager.insert_records(table_name, records, batch_size=1000)
            
            logger.info(
                f"记录存储完成：{business_type_id} -> {table_name}，"
                f"成功{success}条，失败{failed}条"
            )
            
            return success, failed, table_name
            
        except Exception as e:
            logger.error(f"记录存储失败：{business_type_id}，错误：{e}")
            return 0, len(records), table_name


def store_records(
    business_type_id: str,
    records: List[Dict[str, Any]]
) -> Tuple[int, int, str]:
    """
    便利函数：存储清洗后的记录
    
    Args:
        business_type_id: 业务类型ID
        records: 清洗后的记录列表
    
    Returns:
        (成功数, 失败数, 目标表名)
    
    示例：
        success, failed, table = store_records('EC_GOODS_PHONE', cleaned_records)
    """
    return StorageStrategy.store_records(business_type_id, records)
