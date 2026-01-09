# -*- coding: utf-8 -*-
"""
元数据验证模块

验证元数据格式、业务类型有效性、字段完整性
"""

from typing import Dict, Any, Optional, List
from src.utils.logger import get_logger
from src.utils.validation import Validator

logger = get_logger(__name__)


class MetadataValidator:
    """
    元数据验证器
    
    负责：
    1. 验证元数据格式是否完整
    2. 验证业务类型ID是否有效
    3. 验证数据结构类型
    4. 验证必填字段
    """
    
    # 必填字段列表
    REQUIRED_FIELDS = [
        'business_type_id',
        'data_carrier_type',
        'data_structure_type',
        'crawl_date',
        'source_url'
    ]
    
    # 有效的业务类型ID
    VALID_BUSINESS_TYPES = [
        'EC_GOODS_PHONE',      # 业务类型_1
        'EC_COMMENT',          # 业务类型_2
        'CUSTOMER_DIALOG',     # 业务类型_14
        'SOCIAL_COMMENT',      # 业务类型_3
        'SOCIAL_POST',         # 业务类型_4
        'NEWS_ARTICLE',        # 业务类型_5
        'FINANCE_REPORT',      # 业务类型_6
        'ENTERPRISE_INFO',     # 业务类型_7
        'RECRUIT_JOB',         # 业务类型_8
        'VIDEO_METADATA',      # 业务类型_9
        'USER_PROFILE',        # 业务类型_10
        'PROPERTY_INFO',       # 业务类型_11
        'CAR_INFO',            # 业务类型_12
        'PURCHASE_ORDER',      # 业务类型_13
    ]
    
    # 有效的数据结构类型
    VALID_STRUCTURE_TYPES = [
        'structured',           # 结构化
        'semi_structured',      # 半结构化
        'unstructured'          # 非结构化
    ]
    
    @staticmethod
    def validate(metadata: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证元数据
        
        Args:
            metadata: 元数据字典
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必填字段
        for field in MetadataValidator.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"缺少必填字段：{field}")
        
        if errors:
            return False, errors
        
        # 验证业务类型ID
        business_type_id = metadata.get('business_type_id')
        if business_type_id not in MetadataValidator.VALID_BUSINESS_TYPES:
            errors.append(f"无效的业务类型ID：{business_type_id}")
        
        # 验证数据结构类型
        structure_type = metadata.get('data_structure_type')
        if structure_type not in MetadataValidator.VALID_STRUCTURE_TYPES:
            errors.append(f"无效的数据结构类型：{structure_type}")
        
        # 验证日期格式
        crawl_date = metadata.get('crawl_date')
        if not Validator.validate_pattern(crawl_date, r'^\d{8}$'):
            errors.append(f"无效的爬取日期格式：{crawl_date}，应为YYYYMMDD")
        
        if errors:
            return False, errors
        
        logger.info(f"元数据验证通过：{business_type_id}")
        return True, []
    
    @staticmethod
    def get_business_type_id(metadata: Dict[str, Any]) -> Optional[str]:
        """获取业务类型ID"""
        return metadata.get('business_type_id')
    
    @staticmethod
    def get_data_carrier_type(metadata: Dict[str, Any]) -> Optional[str]:
        """获取数据载体类型"""
        return metadata.get('data_carrier_type')
    
    @staticmethod
    def get_crawl_date(metadata: Dict[str, Any]) -> Optional[str]:
        """获取爬取日期"""
        return metadata.get('crawl_date')
