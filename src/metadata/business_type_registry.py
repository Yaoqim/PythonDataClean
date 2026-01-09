# -*- coding: utf-8 -*-
"""
业务类型注册模块

负责业务类型的注册、查询、配置管理。

本项目支持3个核心业务类型（其他业务类型为占位）：
1. EC_GOODS_PHONE - 电商商品信息
2. EC_COMMENT - 电商商品评论
3. CUSTOMER_DIALOG - 客户对话
"""

from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BusinessTypeRegistry:
    """
    业务类型注册表
    
    负责管理所有支持的业务类型及其配置
    """
    
    # 业务类型注册表（仅包含3个核心业务类型的完整配置）
    REGISTRY = {
        # ============================================================
        # 1. 电商商品信息 (EC_GOODS_PHONE)
        # ============================================================
        'EC_GOODS_PHONE': {
            'business_type_name': '电商商品信息',
            'business_type_id': 'EC_GOODS_PHONE',
            'description': '来自电商平台的商品基础信息，包括商品名称、价格、品牌、评分等',
            'data_structure_type': '结构化',
            'table_name': 'ec_product_info',
            'primary_key': 'product_id',
            'core_fields': ['product_id', 'title', 'price', 'currency_code', 'shop_name', 'source_platform'],
            'storage_config': {
                'table_name': 'ec_product_info',
                'primary_key': 'product_id',
                'fields': {
                    'product_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'title': {'type': 'VARCHAR(500)', 'nullable': False},
                    'price': {'type': 'DECIMAL(10,2)', 'nullable': True},
                    'currency_code': {'type': 'VARCHAR(10)', 'nullable': True},
                    'shop_name': {'type': 'VARCHAR(200)', 'nullable': True},
                    'source_platform': {'type': 'VARCHAR(50)', 'nullable': True},
                }
            },
            'clean_config': {
                'must_clean_fields': ['product_id', 'title'],
                'dedup_key': 'product_id',
                'field_standard_rule': {
                    'title': 'strip, remove_special_chars',
                    'price': 'to_float',
                },
            }
        },
        
        # ============================================================
        # 2. 电商商品评论 (EC_COMMENT)
        # ============================================================
        'EC_COMMENT': {
            'business_type_name': '电商商品评论',
            'business_type_id': 'EC_COMMENT',
            'description': '来自电商平台的商品用户评论，包括评论内容、评分、日期等',
            'data_structure_type': '结构化',
            'table_name': 'ec_comment_2024',
            'primary_key': 'comment_id',
            'core_fields': ['comment_id', 'product_id', 'user_name', 'comment_content', 'rating_score', 'comment_date'],
            'storage_config': {
                'table_name': 'ec_comment_2024',
                'primary_key': 'comment_id',
                'fields': {
                    'comment_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'product_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'user_name': {'type': 'VARCHAR(100)', 'nullable': False},
                    'comment_content': {'type': 'TEXT', 'nullable': False},
                    'rating_score': {'type': 'INT', 'nullable': True},
                    'comment_date': {'type': 'DATETIME', 'nullable': True},
                }
            },
            'clean_config': {
                'must_clean_fields': ['comment_id', 'product_id', 'comment_content'],
                'dedup_key': 'comment_id',
                'field_standard_rule': {
                    'comment_content': 'remove_html, remove_url, remove_emoji',
                    'rating_score': 'to_int, validate_range(1,5)',
                },
            }
        },
        
        # ============================================================
        # 3. 客户对话 (CUSTOMER_DIALOG)
        # ============================================================
        'CUSTOMER_DIALOG': {
            'business_type_name': '客户对话',
            'business_type_id': 'CUSTOMER_DIALOG',
            'description': '客户与服务人员的对话记录，包括消息内容、时间戳、对话方等',
            'data_structure_type': '结构化',
            'table_name': 'customer_conversation',
            'primary_key': 'conversation_id',
            'core_fields': ['conversation_id', 'customer_id', 'service_id', 'message_content', 'message_time'],
            'storage_config': {
                'table_name': 'customer_conversation',
                'primary_key': 'conversation_id',
                'fields': {
                    'conversation_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'customer_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'service_id': {'type': 'VARCHAR(100)', 'nullable': False},
                    'message_content': {'type': 'TEXT', 'nullable': False},
                    'message_time': {'type': 'DATETIME', 'nullable': False},
                }
            },
            'clean_config': {
                'must_clean_fields': ['conversation_id', 'message_content'],
                'dedup_key': 'conversation_id',
                'field_standard_rule': {
                    'message_content': 'remove_emoji, remove_url',
                },
            }
        },
    }
    
    @staticmethod
    def register(business_type_id: str, config: Dict[str, Any]) -> bool:
        """
        注册新的业务类型
        
        Args:
            business_type_id: 业务类型ID（唯一）
            config: 业务类型配置字典
        
        Returns:
            True表示注册成功，False表示失败
        """
        if business_type_id in BusinessTypeRegistry.REGISTRY:
            logger.warning(f"业务类型已存在，无法重复注册：{business_type_id}")
            return False
        
        # 验证配置
        required_keys = {'business_type_name', 'description', 'table_name', 'primary_key'}
        missing_keys = required_keys - set(config.keys())
        
        if missing_keys:
            logger.error(f"业务类型配置缺失必需字段：{missing_keys}")
            return False
        
        BusinessTypeRegistry.REGISTRY[business_type_id] = config
        logger.info(f"业务类型注册成功：{business_type_id}")
        return True
    
    @staticmethod
    def get(business_type_id: str) -> Optional[Dict[str, Any]]:
        """
        获取业务类型配置
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            业务类型配置字典，如果不存在返回None
        """
        config = BusinessTypeRegistry.REGISTRY.get(business_type_id)
        
        if config is None:
            logger.warning(f"业务类型不存在或未注册：{business_type_id}")
            return None
        
        return config
    
    @staticmethod
    def exists(business_type_id: str) -> bool:
        """
        检查业务类型是否已注册
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            True表示已注册，False表示未注册
        """
        return business_type_id in BusinessTypeRegistry.REGISTRY
    
    @staticmethod
    def get_all() -> Dict[str, Dict[str, Any]]:
        """
        获取所有已注册的业务类型
        
        Returns:
            业务类型字典（ID -> 配置）
        """
        return BusinessTypeRegistry.REGISTRY.copy()
    
    @staticmethod
    def get_table_name(business_type_id: str) -> Optional[str]:
        """
        获取业务类型对应的表名
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            表名，如果业务类型不存在返回None
        """
        config = BusinessTypeRegistry.get(business_type_id)
        if config:
            return config.get('table_name')
        return None
    
    @staticmethod
    def get_primary_key(business_type_id: str) -> Optional[str]:
        """
        获取业务类型对应的主键字段
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            主键字段名，如果业务类型不存在返回None
        """
        config = BusinessTypeRegistry.get(business_type_id)
        if config:
            return config.get('primary_key')
        return None
    
    @staticmethod
    def get_core_fields(business_type_id: str) -> Optional[list]:
        """
        获取业务类型的核心字段列表
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            核心字段列表，如果业务类型不存在返回None
        """
        config = BusinessTypeRegistry.get(business_type_id)
        if config:
            return config.get('core_fields', [])
        return None
    
    @staticmethod
    def list_all_business_types() -> list:
        """
        获取所有业务类型ID列表
        
        Returns:
            业务类型ID列表
        """
        return list(BusinessTypeRegistry.REGISTRY.keys())


def get_business_type_config(business_type_id: str) -> Optional[Dict[str, Any]]:
    """
    便利函数：获取业务类型配置
    
    Args:
        business_type_id: 业务类型ID
    
    Returns:
        业务类型配置字典
    
    示例：
        config = get_business_type_config('EC_GOODS_PHONE')
        table_name = config['table_name']
    """
    return BusinessTypeRegistry.get(business_type_id)


def register_business_type(business_type_id: str, config: Dict[str, Any]) -> bool:
    """
    便利函数：注册新业务类型
    
    Args:
        business_type_id: 业务类型ID
        config: 配置字典
    
    Returns:
        是否注册成功
    """
    return BusinessTypeRegistry.register(business_type_id, config)
