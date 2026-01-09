# -*- coding: utf-8 -*-
"""
数据验证模块

提供各种数据验证功能，支持：
- 范围检查
- 正则表达式验证
- 一致性检查
- 格式验证
"""

import re
from typing import Any, Union, List, Pattern, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Validator:
    """
    数据验证器
    
    提供多种验证方法
    """
    
    @staticmethod
    def validate_range(
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        value_name: str = "value"
    ) -> bool:
        """
        验证数值是否在指定范围内
        
        Args:
            value: 要验证的数值
            min_value: 最小值（包含）
            max_value: 最大值（包含）
            value_name: 值的名称（用于错误信息）
        
        Returns:
            True表示在范围内，False表示超出范围
        """
        if min_value is not None and value < min_value:
            logger.warning(
                f"{value_name} 超出下限：{value} < {min_value}"
            )
            return False
        
        if max_value is not None and value > max_value:
            logger.warning(
                f"{value_name} 超出上限：{value} > {max_value}"
            )
            return False
        
        return True
    
    @staticmethod
    def validate_pattern(
        text: str,
        pattern: Union[str, Pattern],
        pattern_name: str = "pattern",
        must_match: bool = True
    ) -> bool:
        """
        验证文本是否匹配正则表达式
        
        Args:
            text: 要验证的文本
            pattern: 正则表达式（字符串或编译后的Pattern对象）
            pattern_name: 模式名称（用于错误信息）
            must_match: True表示必须匹配，False表示必须不匹配
        
        Returns:
            验证结果
        """
        try:
            if isinstance(pattern, str):
                pattern = re.compile(pattern)
            
            matched = bool(pattern.match(text))
            
            if must_match and not matched:
                logger.warning(
                    f"文本不匹配 {pattern_name}：{text}"
                )
                return False
            
            if not must_match and matched:
                logger.warning(
                    f"文本不应匹配 {pattern_name}：{text}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"正则表达式验证失败：{e}")
            return False
    
    @staticmethod
    def validate_consistency(
        record: dict,
        consistency_rules: dict
    ) -> bool:
        """
        验证记录的字段一致性
        
        Args:
            record: 要验证的记录字典
            consistency_rules: 一致性规则字典
                              例如：{"price": {"min": 0}, "rating": {"range": (0, 5)}}
        
        Returns:
            True表示一致，False表示不一致
        """
        for field, rule in consistency_rules.items():
            if field not in record:
                logger.warning(f"字段缺失：{field}")
                return False
            
            value = record[field]
            
            # 范围检查
            if "range" in rule:
                min_val, max_val = rule["range"]
                if not Validator.validate_range(value, min_val, max_val, field):
                    return False
            
            # 最小值检查
            if "min" in rule:
                if value < rule["min"]:
                    logger.warning(
                        f"字段 {field} 低于最小值：{value} < {rule['min']}"
                    )
                    return False
            
            # 最大值检查
            if "max" in rule:
                if value > rule["max"]:
                    logger.warning(
                        f"字段 {field} 超过最大值：{value} > {rule['max']}"
                    )
                    return False
        
        return True
    
    @staticmethod
    def validate_required_fields(
        record: dict,
        required_fields: List[str]
    ) -> bool:
        """
        验证必填字段是否都存在
        
        Args:
            record: 记录字典
            required_fields: 必填字段列表
        
        Returns:
            True表示所有必填字段都存在，False表示有缺失
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in record or record[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"缺失必填字段：{missing_fields}")
            return False
        
        return True
    
    @staticmethod
    def validate_field_type(
        value: Any,
        expected_type: Union[type, tuple],
        field_name: str = "field"
    ) -> bool:
        """
        验证字段类型
        
        Args:
            value: 值
            expected_type: 期望的类型（或类型元组）
            field_name: 字段名称
        
        Returns:
            True表示类型正确，False表示类型错误
        """
        if not isinstance(value, expected_type):
            logger.warning(
                f"字段 {field_name} 类型错误：{type(value)}, "
                f"期望类型：{expected_type}"
            )
            return False
        
        return True


# 便利函数
def validate_range(
    value: Union[int, float],
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    value_name: str = "value"
) -> bool:
    """
    快速范围验证
    """
    return Validator.validate_range(value, min_value, max_value, value_name)


def validate_pattern(
    text: str,
    pattern: Union[str, Pattern],
    pattern_name: str = "pattern",
    must_match: bool = True
) -> bool:
    """
    快速模式验证
    """
    return Validator.validate_pattern(text, pattern, pattern_name, must_match)
