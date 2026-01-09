# -*- coding: utf-8 -*-
"""
标准化策略模块

负责将数据字段转为标准格式。

标准化类型：
- 文本字段：去空格、去特殊字符、统一大小写
- 数值字段：去除单位、转为标准数字型
- 时间字段：统一转为标准时间格式
- 标签字段：相似标签归一化
"""

from typing import Any, Dict, Optional, List, Callable
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils

logger = get_logger(__name__)


class NormalizationStrategy:
    """标准化策略"""
    
    @staticmethod
    def normalize_text(text: str, lowercase: bool = False, max_length: Optional[int] = None) -> str:
        """
        标准化文本字段
        
        Args:
            text: 输入文本
            lowercase: 是否转为小写
            max_length: 最大长度（超出则截断）
        
        Returns:
            标准化后的文本
        """
        if not text:
            return text
        
        # 去空格和特殊字符
        text = StringUtils.clean_text(
            text,
            remove_html=True,
            remove_urls=True,
            remove_emoji=True,
            remove_mentions=True,
            max_length=max_length
        )
        
        # 统一大小写
        if lowercase:
            text = text.lower()
        
        return text
    
    @staticmethod
    def normalize_numeric(value: Any, decimal_places: int = 2) -> Optional[float]:
        """
        标准化数值字段
        
        Args:
            value: 输入值（可能是字符串、int、float等）
            decimal_places: 小数位数
        
        Returns:
            标准化后的数值，如转换失败返回None
        """
        if value is None or value == '':
            return None
        
        try:
            # 如果是字符串，移除特殊字符后转换
            if isinstance(value, str):
                # 移除常见的特殊字符（如货币符号、逗号等）
                value = value.replace('¥', '').replace('$', '').replace(',', '').strip()
            
            # 转为float
            numeric_value = float(value)
            
            # 四舍五入到指定小数位
            return round(numeric_value, decimal_places)
            
        except (ValueError, TypeError) as e:
            logger.debug(f"数值转换失败：{value}，错误：{e}")
            return None
    
    @staticmethod
    def normalize_timestamp(timestamp_str: str, target_format: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
        """
        标准化时间字段
        
        Args:
            timestamp_str: 时间戳字符串
            target_format: 目标格式
        
        Returns:
            标准化后的时间字符串
        """
        if not timestamp_str:
            return None
        
        return TimeUtils.standardize_timestamp(timestamp_str, target_format)
    
    @staticmethod
    def normalize_category(
        value: str,
        category_mapping: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        标准化分类字段
        
        Args:
            value: 输入值
            category_mapping: 分类映射字典（可选，用于相似分类的归一化）
        
        Returns:
            标准化后的分类值
        
        示例：
            mapping = {'男': '男性', 'M': '男性', 'F': '女性', '女': '女性'}
            result = normalize_category('男', mapping)  # 返回 '男性'
        """
        if not value:
            return None
        
        value = value.strip()
        
        # 如果提供了映射，优先使用映射
        if category_mapping and value in category_mapping:
            return category_mapping[value]
        
        # 否则原样返回
        return value
    
    @staticmethod
    def normalize_record(
        record: Dict[str, Any],
        normalization_rules: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        根据规则标准化整条记录
        
        Args:
            record: 原始记录
            normalization_rules: 标准化规则字典
        
        Returns:
            标准化后的记录
        
        规则格式示例：
        {
            'name': {'type': 'text', 'lowercase': True, 'max_length': 100},
            'price': {'type': 'numeric', 'decimal_places': 2},
            'created_time': {'type': 'timestamp', 'format': '%Y-%m-%d'},
            'category': {'type': 'category', 'mapping': {'A': 'Category A'}}
        }
        """
        normalized = {}
        
        for field_name, value in record.items():
            if field_name not in normalization_rules:
                # 无规则的字段原样保留
                normalized[field_name] = value
                continue
            
            rule = normalization_rules[field_name]
            field_type = rule.get('type', 'text')
            
            try:
                if field_type == 'text':
                    lowercase = rule.get('lowercase', False)
                    max_length = rule.get('max_length')
                    normalized[field_name] = NormalizationStrategy.normalize_text(
                        str(value) if value is not None else '',
                        lowercase=lowercase,
                        max_length=max_length
                    )
                
                elif field_type == 'numeric':
                    decimal_places = rule.get('decimal_places', 2)
                    normalized[field_name] = NormalizationStrategy.normalize_numeric(
                        value,
                        decimal_places=decimal_places
                    )
                
                elif field_type == 'timestamp':
                    target_format = rule.get('format', '%Y-%m-%d %H:%M:%S')
                    normalized[field_name] = NormalizationStrategy.normalize_timestamp(
                        str(value) if value is not None else '',
                        target_format=target_format
                    )
                
                elif field_type == 'category':
                    category_mapping = rule.get('mapping')
                    normalized[field_name] = NormalizationStrategy.normalize_category(
                        str(value) if value is not None else '',
                        category_mapping=category_mapping
                    )
                
                else:
                    logger.warning(f"未知的字段类型：{field_type}，字段原样保留")
                    normalized[field_name] = value
                    
            except Exception as e:
                logger.warning(f"字段{field_name}标准化失败：{e}，原样保留")
                normalized[field_name] = value
        
        return normalized


def normalize_field(
    value: Any,
    field_type: str,
    **kwargs
) -> Any:
    """
    便利函数：标准化单个字段值
    
    Args:
        value: 字段值
        field_type: 字段类型（text/numeric/timestamp/category）
        **kwargs: 类型特定的参数
    
    Returns:
        标准化后的值
    
    示例：
        # 标准化文本
        result = normalize_field("hello WORLD", "text", lowercase=True)
        
        # 标准化数值
        result = normalize_field("¥99.99", "numeric", decimal_places=2)
        
        # 标准化时间
        result = normalize_field("2024-01-08", "timestamp")
    """
    if field_type == 'text':
        lowercase = kwargs.get('lowercase', False)
        max_length = kwargs.get('max_length')
        return NormalizationStrategy.normalize_text(str(value) if value else '', lowercase, max_length)
    
    elif field_type == 'numeric':
        decimal_places = kwargs.get('decimal_places', 2)
        return NormalizationStrategy.normalize_numeric(value, decimal_places)
    
    elif field_type == 'timestamp':
        target_format = kwargs.get('format', '%Y-%m-%d %H:%M:%S')
        return NormalizationStrategy.normalize_timestamp(str(value) if value else '', target_format)
    
    elif field_type == 'category':
        category_mapping = kwargs.get('mapping')
        return NormalizationStrategy.normalize_category(str(value) if value else '', category_mapping)
    
    else:
        logger.warning(f"未知的字段类型：{field_type}")
        return value
