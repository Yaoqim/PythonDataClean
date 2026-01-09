# -*- coding: utf-8 -*-
"""
缺失值处理策略模块

处理数据中的缺失值（NULL、空字符串等）。

处理策略：
- 核心字段：缺失率低时删除记录，缺失率高时标注"待补充"
- 非核心字段：填充为"未知"或使用统计值（众数、中位数）
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MissingValueHandler:
    """缺失值处理器"""
    
    # 缺失值标识
    MISSING_INDICATORS = {None, '', 'null', 'NULL', 'None', 'NONE', '-', 'N/A', 'na', 'unknown'}
    
    @staticmethod
    def is_missing(value: Any) -> bool:
        """
        检查值是否为缺失
        
        Args:
            value: 要检查的值
        
        Returns:
            True表示缺失，False表示非缺失
        """
        if value is None or value == '':
            return True
        
        if isinstance(value, str):
            return value.strip() in MissingValueHandler.MISSING_INDICATORS
        
        return False
    
    @staticmethod
    def calculate_missing_rate(records: List[Dict[str, Any]], field: str) -> float:
        """
        计算字段的缺失率
        
        Args:
            records: 记录列表
            field: 字段名
        
        Returns:
            缺失率（0-1）
        """
        if not records:
            return 0.0
        
        missing_count = sum(
            1 for record in records
            if MissingValueHandler.is_missing(record.get(field))
        )
        
        return missing_count / len(records)
    
    @staticmethod
    def delete_records_with_missing(
        records: List[Dict[str, Any]],
        fields: List[str]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        删除指定字段中有缺失值的记录
        
        Args:
            records: 记录列表
            fields: 字段列表（任何一个字段缺失则删除该记录）
        
        Returns:
            (删除缺失记录后的列表, 删除的记录数)
        """
        if not records or not fields:
            return records, 0
        
        original_count = len(records)
        filtered = []
        
        for record in records:
            # 检查是否有任何字段缺失
            has_missing = False
            for field in fields:
                if MissingValueHandler.is_missing(record.get(field)):
                    has_missing = True
                    break
            
            if not has_missing:
                filtered.append(record)
        
        deleted_count = original_count - len(filtered)
        logger.info(f"删除缺失记录：删除{deleted_count}条，保留{len(filtered)}条")
        
        return filtered, deleted_count
    
    @staticmethod
    def fill_missing_with_value(
        records: List[Dict[str, Any]],
        field: str,
        fill_value: Any
    ) -> List[Dict[str, Any]]:
        """
        用固定值填充缺失值
        
        Args:
            records: 记录列表
            field: 字段名
            fill_value: 填充值
        
        Returns:
            填充后的记录列表
        """
        filled = []
        
        for record in records:
            if MissingValueHandler.is_missing(record.get(field)):
                record[field] = fill_value
            filled.append(record)
        
        logger.debug(f"字段{field}缺失值填充为：{fill_value}")
        return filled
    
    @staticmethod
    def fill_missing_with_mode(
        records: List[Dict[str, Any]],
        field: str
    ) -> List[Dict[str, Any]]:
        """
        用众数（出现频率最高的值）填充缺失值
        
        Args:
            records: 记录列表
            field: 字段名
        
        Returns:
            填充后的记录列表
        """
        # 统计非缺失的值
        values = [
            record.get(field)
            for record in records
            if not MissingValueHandler.is_missing(record.get(field))
        ]
        
        if not values:
            logger.warning(f"字段{field}没有非缺失值，无法计算众数")
            return records
        
        # 计算众数
        value_counts = Counter(values)
        mode_value = value_counts.most_common(1)[0][0]
        
        # 填充
        filled = []
        for record in records:
            if MissingValueHandler.is_missing(record.get(field)):
                record[field] = mode_value
            filled.append(record)
        
        logger.debug(f"字段{field}缺失值填充为众数：{mode_value}")
        return filled
    
    @staticmethod
    def fill_missing_with_mean(
        records: List[Dict[str, Any]],
        field: str,
        decimal_places: int = 2
    ) -> List[Dict[str, Any]]:
        """
        用平均值填充数值字段的缺失值
        
        Args:
            records: 记录列表
            field: 字段名
            decimal_places: 小数位数
        
        Returns:
            填充后的记录列表
        """
        # 提取数值
        values = []
        for record in records:
            value = record.get(field)
            if not MissingValueHandler.is_missing(value):
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    pass
        
        if not values:
            logger.warning(f"字段{field}没有可转换的数值，无法计算平均值")
            return records
        
        # 计算平均值
        mean_value = round(sum(values) / len(values), decimal_places)
        
        # 填充
        filled = []
        for record in records:
            if MissingValueHandler.is_missing(record.get(field)):
                record[field] = mean_value
            filled.append(record)
        
        logger.debug(f"字段{field}缺失值填充为平均值：{mean_value}")
        return filled
    
    @staticmethod
    def handle_records_missing(
        records: List[Dict[str, Any]],
        handling_config: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        根据配置处理缺失值
        
        Args:
            records: 记录列表
            handling_config: 处理配置字典
        
        Returns:
            (处理后的记录列表, 统计信息)
        
        配置格式示例：
        {
            'core_fields': {
                'product_id': 'delete',  # 删除有缺失的记录
                'title': 'fill_with_unknown'  # 填充为"未知"
            },
            'non_core_fields': {
                'price': {'strategy': 'fill_mean'},  # 用平均值填充
                'category': {'strategy': 'fill_mode'},  # 用众数填充
            }
        }
        """
        if not records:
            return [], {'total_records': 0, 'affected_records': 0}
        
        original_count = len(records)
        working_records = [record.copy() for record in records]
        
        stats = {
            'original_records': original_count,
            'deleted_records': 0,
            'filled_fields': {}
        }
        
        # 处理核心字段
        core_config = handling_config.get('core_fields', {})
        for field, strategy in core_config.items():
            if strategy == 'delete':
                # 删除有缺失的记录
                working_records, deleted = MissingValueHandler.delete_records_with_missing(
                    working_records, [field]
                )
                stats['deleted_records'] += deleted
            
            elif strategy == 'fill_with_unknown':
                working_records = MissingValueHandler.fill_missing_with_value(
                    working_records, field, '待补充'
                )
                stats['filled_fields'][field] = '填充为"待补充"'
        
        # 处理非核心字段
        non_core_config = handling_config.get('non_core_fields', {})
        for field, config in non_core_config.items():
            if isinstance(config, dict):
                strategy = config.get('strategy', 'fill_with_unknown')
            else:
                strategy = config
            
            if strategy == 'fill_mean':
                working_records = MissingValueHandler.fill_missing_with_mean(working_records, field)
                stats['filled_fields'][field] = '填充为平均值'
            
            elif strategy == 'fill_mode':
                working_records = MissingValueHandler.fill_missing_with_mode(working_records, field)
                stats['filled_fields'][field] = '填充为众数'
            
            elif strategy == 'fill_with_unknown':
                working_records = MissingValueHandler.fill_missing_with_value(working_records, field, '未知')
                stats['filled_fields'][field] = '填充为"未知"'
        
        stats['final_records'] = len(working_records)
        
        logger.info(
            f"缺失值处理完成：原始{original_count}条，删除{stats['deleted_records']}条，"
            f"最终{len(working_records)}条，处理字段数{len(stats['filled_fields'])}"
        )
        
        return working_records, stats


def handle_missing_values(
    records: List[Dict[str, Any]],
    fields_to_delete: Optional[List[str]] = None,
    fields_to_fill: Optional[Dict[str, Any]] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    便利函数：处理缺失值
    
    Args:
        records: 记录列表
        fields_to_delete: 如果这些字段有缺失则删除该记录
        fields_to_fill: 要填充的字段及填充值
    
    Returns:
        (处理后的记录, 统计信息)
    
    示例：
        # 删除product_id缺失的记录，填充price为0
        result, stats = handle_missing_values(
            records,
            fields_to_delete=['product_id'],
            fields_to_fill={'price': 0}
        )
    """
    if not records:
        return [], {'original_records': 0}
    
    working_records = records.copy()
    stats = {'original_records': len(records)}
    
    # 删除指定字段有缺失的记录
    if fields_to_delete:
        working_records, deleted = MissingValueHandler.delete_records_with_missing(
            working_records, fields_to_delete
        )
        stats['deleted_records'] = deleted
    
    # 填充缺失值
    if fields_to_fill:
        for field, fill_value in fields_to_fill.items():
            working_records = MissingValueHandler.fill_missing_with_value(
                working_records, field, fill_value
            )
    
    stats['final_records'] = len(working_records)
    return working_records, stats
