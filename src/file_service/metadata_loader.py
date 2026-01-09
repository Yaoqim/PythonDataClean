# -*- coding: utf-8 -*-
"""
元数据加载模块

负责加载和验证`.metadata.json`文件。

元数据结构（参考《项目规范.md》）：
{
  "business_type_id": "EC_GOODS_PHONE",
  "data_structure_type": "结构化",
  "file_size_mb": 50,
  "data_carrier_type": "JSON",
  "estimated_record_count": 10000,
  "crawl_date": "20240108",
  "data_source": "京东商城",
  "actual_record_count": 9856,
  "crawl_tool": "Scrapy",
  "checksum": "abc123def456"
}
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger
from src.file_service.file_handler import FileHandler

logger = get_logger(__name__)


class MetadataLoader:
    """
    元数据加载器
    
    负责：
    1. 自动查找元数据文件（同名的.metadata.json）
    2. 加载和验证元数据
    3. 提供元数据查询接口
    """
    
    # 元数据文件后缀
    METADATA_SUFFIX = '.metadata.json'
    
    # 必需字段
    REQUIRED_FIELDS = {
        'business_type_id',
        'data_structure_type',
        'file_size_mb',
        'data_carrier_type',
    }
    
    # 可选字段
    OPTIONAL_FIELDS = {
        'estimated_record_count',
        'crawl_date',
        'data_source',
        'actual_record_count',
        'crawl_tool',
        'checksum',
        'description',
    }
    
    @staticmethod
    def find_metadata_file(data_file_path: str) -> Optional[str]:
        """
        查找数据文件对应的元数据文件
        
        元数据文件命名规则：{data_file}.metadata.json
        
        例：
        - 数据文件：EC_GOODS_PHONE_20240108_0001.json
        - 元数据文件：EC_GOODS_PHONE_20240108_0001.json.metadata.json
        
        Args:
            data_file_path: 数据文件路径
        
        Returns:
            元数据文件路径，如果找不到返回None
        """
        metadata_path = f"{data_file_path}{MetadataLoader.METADATA_SUFFIX}"
        
        if FileHandler.check_file_exists(metadata_path):
            return metadata_path
        
        # 尝试另一种命名方式（不包含原扩展名）
        path = Path(data_file_path)
        base_name = path.stem  # 去掉扩展名
        metadata_path_alt = path.parent / f"{base_name}{MetadataLoader.METADATA_SUFFIX}"
        
        if metadata_path_alt.exists():
            return str(metadata_path_alt)
        
        logger.warning(f"未找到元数据文件：{data_file_path}")
        return None
    
    @staticmethod
    def load_metadata(metadata_file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载元数据文件
        
        Args:
            metadata_file_path: 元数据文件路径
        
        Returns:
            元数据字典，如果加载失败返回None
        """
        try:
            if not FileHandler.check_file_exists(metadata_file_path):
                return None
            
            text = FileHandler.read_file_text(metadata_file_path)
            if text is None:
                return None
            
            metadata = json.loads(text)
            
            # 验证元数据
            if not MetadataLoader._validate_metadata(metadata):
                return None
            
            logger.info(f"成功加载元数据：{metadata_file_path}")
            return metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"元数据JSON解析失败：{metadata_file_path}，错误：{e}")
            return None
        except Exception as e:
            logger.error(f"加载元数据失败：{metadata_file_path}，错误：{e}")
            return None
    
    @staticmethod
    def load_from_data_file(data_file_path: str) -> Optional[Dict[str, Any]]:
        """
        自动查找并加载数据文件对应的元数据
        
        Args:
            data_file_path: 数据文件路径
        
        Returns:
            元数据字典，如果找不到或加载失败返回None
        """
        # 查找元数据文件
        metadata_path = MetadataLoader.find_metadata_file(data_file_path)
        if metadata_path is None:
            return None
        
        # 加载元数据
        return MetadataLoader.load_metadata(metadata_path)
    
    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]) -> bool:
        """
        验证元数据完整性
        
        Args:
            metadata: 元数据字典
        
        Returns:
            True表示有效，False表示无效
        """
        # 检查必需字段
        missing_fields = MetadataLoader.REQUIRED_FIELDS - set(metadata.keys())
        if missing_fields:
            logger.error(f"元数据缺失必需字段：{missing_fields}")
            return False
        
        # 检查业务类型ID格式
        business_type_id = metadata.get('business_type_id', '')
        if not business_type_id or not isinstance(business_type_id, str):
            logger.error(f"业务类型ID无效：{business_type_id}")
            return False
        
        # 检查数据结构类型
        data_structure_type = metadata.get('data_structure_type', '')
        valid_types = {'结构化', '半结构化', '非结构化'}
        if data_structure_type not in valid_types:
            logger.error(f"数据结构类型无效：{data_structure_type}，必须是{valid_types}")
            return False
        
        # 检查数据载体类型
        data_carrier_type = metadata.get('data_carrier_type', '')
        valid_carriers = {'JSON', 'CSV', 'TXT', 'XML', 'HTML', 'PDF'}
        if data_carrier_type not in valid_carriers:
            logger.error(f"数据载体类型无效：{data_carrier_type}，必须是{valid_carriers}")
            return False
        
        # 检查文件大小
        file_size_mb = metadata.get('file_size_mb', 0)
        if not isinstance(file_size_mb, (int, float)) or file_size_mb < 0:
            logger.error(f"文件大小无效：{file_size_mb}")
            return False
        
        # 检查记录数（如果存在）
        if 'estimated_record_count' in metadata:
            count = metadata['estimated_record_count']
            if not isinstance(count, int) or count < 0:
                logger.error(f"估计记录数无效：{count}")
                return False
        
        return True
    
    @staticmethod
    def extract_business_type(metadata: Dict[str, Any]) -> Optional[str]:
        """
        从元数据中提取业务类型ID
        
        Args:
            metadata: 元数据字典
        
        Returns:
            业务类型ID
        """
        return metadata.get('business_type_id')
    
    @staticmethod
    def extract_data_structure_type(metadata: Dict[str, Any]) -> Optional[str]:
        """
        从元数据中提取数据结构类型
        
        Args:
            metadata: 元数据字典
        
        Returns:
            数据结构类型（结构化/半结构化/非结构化）
        """
        return metadata.get('data_structure_type')
    
    @staticmethod
    def extract_file_size_mb(metadata: Dict[str, Any]) -> float:
        """
        从元数据中提取文件大小
        
        Args:
            metadata: 元数据字典
        
        Returns:
            文件大小（MB）
        """
        return metadata.get('file_size_mb', 0.0)
    
    @staticmethod
    def extract_estimated_record_count(metadata: Dict[str, Any]) -> int:
        """
        从元数据中提取估计记录数
        
        Args:
            metadata: 元数据字典
        
        Returns:
            估计记录数，如果不存在返回0
        """
        return metadata.get('estimated_record_count', 0)


def load_metadata(metadata_file_path: str) -> Optional[Dict[str, Any]]:
    """
    便利函数：加载元数据文件
    
    Args:
        metadata_file_path: 元数据文件路径
    
    Returns:
        元数据字典
    
    示例：
        metadata = load_metadata("data.json.metadata.json")
        business_type = metadata['business_type_id']
    """
    return MetadataLoader.load_metadata(metadata_file_path)
