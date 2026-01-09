# -*- coding: utf-8 -*-
"""
清洗器工厂

负责根据业务类型ID创建对应的清洗器实例。

工厂模式优点：
- 集中管理所有清洗器的创建
- 支持动态注册新的清洗器
- 提供统一的清洗器获取接口
"""

from typing import Optional, Dict, Type
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CleanerFactory:
    """清洗器工厂"""
    
    # 清洗器注册表（业务类型ID -> 清洗器类）
    _registry: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, business_type_id: str, cleaner_class: Type) -> None:
        """
        注册清洗器
        
        Args:
            business_type_id: 业务类型ID
            cleaner_class: 清洗器类
        """
        cls._registry[business_type_id] = cleaner_class
        logger.info(f"清洗器已注册：{business_type_id} -> {cleaner_class.__name__}")
    
    @classmethod
    def create(cls, business_type_id: str):
        """
        创建清洗器实例
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            清洗器实例，如业务类型不支持返回None
        """
        if business_type_id not in cls._registry:
            logger.warning(f"不支持的业务类型：{business_type_id}")
            return None
        
        cleaner_class = cls._registry[business_type_id]
        
        try:
            instance = cleaner_class()
            logger.debug(f"清洗器创建成功：{business_type_id}")
            return instance
        except Exception as e:
            logger.error(f"清洗器创建失败：{business_type_id}，错误：{e}")
            return None
    
    @classmethod
    def get_supported_types(cls):
        """获取所有支持的业务类型"""
        return list(cls._registry.keys())
    
    @classmethod
    def is_supported(cls, business_type_id: str) -> bool:
        """检查业务类型是否支持"""
        return business_type_id in cls._registry


def get_cleaner(business_type_id: str):
    """
    便利函数：获取清洗器实例
    
    Args:
        business_type_id: 业务类型ID
    
    Returns:
        清洗器实例
    
    示例：
        cleaner = get_cleaner('EC_GOODS_PHONE')
        records, stats = cleaner.clean(data)
    """
    return CleanerFactory.create(business_type_id)
