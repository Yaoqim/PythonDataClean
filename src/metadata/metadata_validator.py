# -*- coding: utf-8 -*-
"""
元数据验证模块

负责验证业务流程中各阶段的数据和配置。

验证范围：
1. 输入元数据文件格式和完整性
2. 清洗规则配置有效性
3. 业务类型注册有效性
4. 清洗结果有效性
"""

from typing import Dict, Any, List, Optional, Tuple
from src.utils.logger import get_logger
from src.utils.validation import Validator

logger = get_logger(__name__)


class MetadataValidator:
    """
    元数据验证器
    
    负责验证项目中各类元数据的有效性
    """
    
    # 支持的数据结构类型
    VALID_DATA_STRUCTURES = {'结构化', '半结构化', '非结构化'}
    
    # 支持的数据载体类型
    VALID_DATA_CARRIERS = {'JSON', 'CSV', 'TXT', 'XML', 'HTML', 'PDF', 'JSONL'}
    
    # 支持的业务类型（3个核心业务类型）
    VALID_BUSINESS_TYPES = {
        'EC_GOODS_PHONE',        # 电商商品信息
        'EC_COMMENT',            # 电商商品评论
        'CUSTOMER_DIALOG',       # 客户对话
    }
    
    @staticmethod
    def validate_business_type(business_type_id: str) -> bool:
        """
        验证业务类型ID是否有效
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            True表示有效，False表示无效
        """
        if not business_type_id or not isinstance(business_type_id, str):
            logger.warning(f"业务类型ID无效（非字符串或为空）：{business_type_id}")
            return False
        
        if business_type_id not in MetadataValidator.VALID_BUSINESS_TYPES:
            logger.warning(
                f"业务类型ID不支持：{business_type_id}，"
                f"支持的类型：{MetadataValidator.VALID_BUSINESS_TYPES}"
            )
            return False
        
        return True
    
    @staticmethod
    def validate_data_structure_type(data_structure_type: str) -> bool:
        """
        验证数据结构类型是否有效
        
        Args:
            data_structure_type: 数据结构类型（结构化/半结构化/非结构化）
        
        Returns:
            True表示有效，False表示无效
        """
        if not data_structure_type or not isinstance(data_structure_type, str):
            logger.warning(f"数据结构类型无效：{data_structure_type}")
            return False
        
        if data_structure_type not in MetadataValidator.VALID_DATA_STRUCTURES:
            logger.warning(
                f"数据结构类型不支持：{data_structure_type}，"
                f"支持的类型：{MetadataValidator.VALID_DATA_STRUCTURES}"
            )
            return False
        
        return True
    
    @staticmethod
    def validate_data_carrier_type(data_carrier_type: str) -> bool:
        """
        验证数据载体类型是否有效
        
        Args:
            data_carrier_type: 数据载体类型（JSON/CSV/HTML等）
        
        Returns:
            True表示有效，False表示无效
        """
        if not data_carrier_type or not isinstance(data_carrier_type, str):
            logger.warning(f"数据载体类型无效：{data_carrier_type}")
            return False
        
        if data_carrier_type not in MetadataValidator.VALID_DATA_CARRIERS:
            logger.warning(
                f"数据载体类型不支持：{data_carrier_type}，"
                f"支持的类型：{MetadataValidator.VALID_DATA_CARRIERS}"
            )
            return False
        
        return True
    
    @staticmethod
    def validate_file_size(file_size_mb: float) -> bool:
        """
        验证文件大小是否有效
        
        Args:
            file_size_mb: 文件大小（MB）
        
        Returns:
            True表示有效，False表示无效
        """
        if not isinstance(file_size_mb, (int, float)):
            logger.warning(f"文件大小类型错误：{type(file_size_mb)}")
            return False
        
        if file_size_mb < 0:
            logger.warning(f"文件大小不能为负：{file_size_mb}")
            return False
        
        return True
    
    @staticmethod
    def validate_record_count(record_count: int) -> bool:
        """
        验证记录数是否有效
        
        Args:
            record_count: 记录数
        
        Returns:
            True表示有效，False表示无效
        """
        if not isinstance(record_count, int):
            logger.warning(f"记录数类型错误：{type(record_count)}")
            return False
        
        if record_count < 0:
            logger.warning(f"记录数不能为负：{record_count}")
            return False
        
        return True
    
    @staticmethod
    def validate_clean_config(clean_config: Dict[str, Any]) -> bool:
        """
        验证清洗配置的有效性
        
        Args:
            clean_config: 清洗配置字典
        
        Returns:
            True表示有效，False表示无效
        """
        if not isinstance(clean_config, dict):
            logger.warning(f"清洗配置类型错误：{type(clean_config)}")
            return False
        
        # 检查必需字段
        required_keys = {'must_clean_fields', 'field_standard_rule'}
        missing_keys = required_keys - set(clean_config.keys())
        
        if missing_keys:
            logger.warning(f"清洗配置缺失必需字段：{missing_keys}")
            return False
        
        # 验证must_clean_fields是列表
        must_clean_fields = clean_config.get('must_clean_fields')
        if not isinstance(must_clean_fields, list):
            logger.warning(f"must_clean_fields应为列表，实际：{type(must_clean_fields)}")
            return False
        
        # 验证field_standard_rule是字典
        field_standard_rule = clean_config.get('field_standard_rule')
        if not isinstance(field_standard_rule, dict):
            logger.warning(f"field_standard_rule应为字典，实际：{type(field_standard_rule)}")
            return False
        
        return True
    
    @staticmethod
    def validate_storage_config(storage_config: Dict[str, Any]) -> bool:
        """
        验证存储配置的有效性
        
        Args:
            storage_config: 存储配置字典
        
        Returns:
            True表示有效，False表示无效
        """
        if not isinstance(storage_config, dict):
            logger.warning(f"存储配置类型错误：{type(storage_config)}")
            return False
        
        # 检查database_config
        if 'database_config' not in storage_config:
            logger.warning("存储配置缺失database_config")
            return False
        
        db_config = storage_config['database_config']
        if not isinstance(db_config, dict):
            logger.warning(f"database_config应为字典，实际：{type(db_config)}")
            return False
        
        # 检查必需的数据库配置字段
        required_db_keys = {'table_name', 'primary_key'}
        missing_db_keys = required_db_keys - set(db_config.keys())
        
        if missing_db_keys:
            logger.warning(f"database_config缺失字段：{missing_db_keys}")
            return False
        
        # 验证表名和主键不为空
        table_name = db_config.get('table_name', '')
        primary_key = db_config.get('primary_key', '')
        
        if not table_name or not isinstance(table_name, str):
            logger.warning(f"表名无效：{table_name}")
            return False
        
        if not primary_key or not isinstance(primary_key, str):
            logger.warning(f"主键无效：{primary_key}")
            return False
        
        return True
    
    @staticmethod
    def validate_cleaned_records(records: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        验证清洗后的记录集合
        
        Args:
            records: 清洗后的记录列表
        
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        if not isinstance(records, list):
            errors.append(f"记录集合应为列表，实际：{type(records)}")
            return False, errors
        
        if len(records) == 0:
            errors.append("记录集合为空")
            return False, errors
        
        # 检查每条记录
        for idx, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"第{idx}条记录不是字典，类型：{type(record)}")
            
            # 检查记录中是否有None字段（可选）
            for field, value in record.items():
                if value is None:
                    logger.debug(f"第{idx}条记录的字段{field}为None")
        
        return len(errors) == 0, errors


def validate_metadata(
    business_type: str,
    data_structure: str,
    data_carrier: str,
    file_size_mb: float
) -> Tuple[bool, List[str]]:
    """
    便利函数：验证元数据的关键字段
    
    Args:
        business_type: 业务类型ID
        data_structure: 数据结构类型
        data_carrier: 数据载体类型
        file_size_mb: 文件大小（MB）
    
    Returns:
        (是否全部有效, 错误信息列表)
    
    示例：
        valid, errors = validate_metadata(
            "EC_GOODS_PHONE",
            "结构化",
            "JSON",
            50.5
        )
    """
    errors = []
    
    if not MetadataValidator.validate_business_type(business_type):
        errors.append(f"业务类型无效：{business_type}")
    
    if not MetadataValidator.validate_data_structure_type(data_structure):
        errors.append(f"数据结构类型无效：{data_structure}")
    
    if not MetadataValidator.validate_data_carrier_type(data_carrier):
        errors.append(f"数据载体类型无效：{data_carrier}")
    
    if not MetadataValidator.validate_file_size(file_size_mb):
        errors.append(f"文件大小无效：{file_size_mb}")
    
    return len(errors) == 0, errors
