# -*- coding: utf-8 -*-
"""
元数据处理模块

负责业务类型注册、元数据验证等功能，是数据清洗流程的关键环节。

模块功能：
1. metadata_validator.py - 元数据验证
2. business_type_registry.py - 业务类型注册和查询
"""

from src.metadata.metadata_validator import MetadataValidator, validate_metadata
from src.metadata.business_type_registry import (
    BusinessTypeRegistry,
    get_business_type_config,
    register_business_type
)

__all__ = [
    "MetadataValidator",
    "validate_metadata",
    "BusinessTypeRegistry",
    "get_business_type_config",
    "register_business_type",
]
