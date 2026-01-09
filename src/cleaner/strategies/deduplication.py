# -*- coding: utf-8 -*-
"""
去重策略模块

负责识别和移除重复记录。

去重原则：
- 按唯一标识（如ID字段）进行完全去重
- 保留第一条记录，删除后续重复记录
- 记录去重统计信息
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeduplicationStrategy:
    """去重策略"""
    
    @staticmethod
    def deduplicate_by_key(
        records: List[Dict[str, Any]],
        key_field: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        按关键字段去重
        
        Args:
            records: 记录列表
            key_field: 关键字段名（用作唯一标识）
        
        Returns:
            (去重后的记录列表, 统计信息)
        
        统计信息包括：
        {
            'original_count': 原始记录数,
            'deduplicated_count': 去重后记录数,
            'duplicate_count': 重复记录数,
            'dedup_rate': 去重率 (0-1)
        }
        """
        if not records:
            return [], {
                'original_count': 0,
                'deduplicated_count': 0,
                'duplicate_count': 0,
                'dedup_rate': 0.0
            }
        
        original_count = len(records)
        seen_keys: Set[Any] = set()
        deduplicated = []
        duplicates = []
        
        for record in records:
            key_value = record.get(key_field)
            
            # 跳过关键字段为空的记录
            if key_value is None or key_value == '':
                deduplicated.append(record)
                continue
            
            # 检查是否已见过此关键值
            if key_value not in seen_keys:
                seen_keys.add(key_value)
                deduplicated.append(record)
            else:
                duplicates.append(record)
        
        duplicate_count = len(duplicates)
        dedup_rate = duplicate_count / original_count if original_count > 0 else 0.0
        
        stats = {
            'original_count': original_count,
            'deduplicated_count': len(deduplicated),
            'duplicate_count': duplicate_count,
            'dedup_rate': round(dedup_rate, 4)
        }
        
        logger.info(
            f"去重完成：原始{original_count}条，去重后{len(deduplicated)}条，"
            f"重复{duplicate_count}条，去重率{dedup_rate:.2%}"
        )
        
        return deduplicated, stats
    
    @staticmethod
    def deduplicate_by_multiple_keys(
        records: List[Dict[str, Any]],
        key_fields: List[str]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        按多个字段组合去重
        
        Args:
            records: 记录列表
            key_fields: 关键字段列表（组合形成唯一标识）
        
        Returns:
            (去重后的记录列表, 统计信息)
        """
        if not records or not key_fields:
            return records, {
                'original_count': len(records),
                'deduplicated_count': len(records),
                'duplicate_count': 0,
                'dedup_rate': 0.0
            }
        
        original_count = len(records)
        seen_combinations: Set[Tuple] = set()
        deduplicated = []
        duplicate_count = 0
        
        for record in records:
            # 构建关键字段的组合
            key_values = tuple(
                record.get(field, '') for field in key_fields
            )
            
            # 检查是否已见过此组合
            if key_values not in seen_combinations:
                seen_combinations.add(key_values)
                deduplicated.append(record)
            else:
                duplicate_count += 1
        
        dedup_rate = duplicate_count / original_count if original_count > 0 else 0.0
        
        stats = {
            'original_count': original_count,
            'deduplicated_count': len(deduplicated),
            'duplicate_count': duplicate_count,
            'dedup_rate': round(dedup_rate, 4)
        }
        
        logger.info(
            f"多键去重完成（字段：{key_fields}）：原始{original_count}条，"
            f"去重后{len(deduplicated)}条，重复{duplicate_count}条"
        )
        
        return deduplicated, stats


def deduplicate_records(
    records: List[Dict[str, Any]],
    key_field: Optional[str] = None,
    key_fields: Optional[List[str]] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    便利函数：去重记录
    
    Args:
        records: 记录列表
        key_field: 单个关键字段
        key_fields: 多个关键字段（优先使用）
    
    Returns:
        (去重后的记录, 统计信息)
    
    示例：
        # 按单个字段去重
        result, stats = deduplicate_records(records, key_field='product_id')
        
        # 按多个字段去重
        result, stats = deduplicate_records(records, key_fields=['user_id', 'product_id'])
    """
    if key_fields:
        return DeduplicationStrategy.deduplicate_by_multiple_keys(records, key_fields)
    elif key_field:
        return DeduplicationStrategy.deduplicate_by_key(records, key_field)
    else:
        logger.warning("未指定关键字段，无法进行去重")
        return records, {'error': '未指定关键字段'}
