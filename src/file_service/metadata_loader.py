# -*- coding: utf-8 -*-
"""
元数据加载模块

加载和解析与数据文件同名的.metadata.json文件
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.encoding_checker import convert_to_utf8

logger = get_logger(__name__)


class MetadataLoader:
    """
    元数据加载器
    
    负责：
    1. 查找与数据文件同名的.metadata.json文件
    2. 加载和解析元数据
    3. 提取关键信息
    """
    
    @staticmethod
    def load_metadata(data_file_path: str) -> Optional[Dict[str, Any]]:
        """
        加载与数据文件对应的元数据
        
        Args:
            data_file_path: 数据文件路径
        
        Returns:
            元数据字典，或None（如果元数据文件不存在）
        
        示例：
            metadata = load_metadata("/data/EC_GOODS_PHONE_20240108_0001.json")
            # 会自动查找 /data/EC_GOODS_PHONE_20240108_0001.metadata.json
        """
        # 生成元数据文件路径
        metadata_path = MetadataLoader._get_metadata_path(data_file_path)
        
        if not os.path.exists(metadata_path):
            logger.warning(f"元数据文件不存在：{metadata_path}")
            return None
        
        try:
            with open(metadata_path, 'rb') as f:
                data_bytes = f.read()
            
            # 检查编码
            text, encoding = convert_to_utf8(data_bytes)
            logger.debug(f"元数据文件编码：{encoding}")
            
            # 解析JSON
            metadata = json.loads(text)
            logger.info(f"成功加载元数据：{metadata_path}")
            return metadata
            
        except Exception as e:
            logger.error(f"元数据加载失败：{metadata_path}，错误：{e}")
            return None
    
    @staticmethod
    def _get_metadata_path(data_file_path: str) -> str:
        """
        根据数据文件路径生成元数据文件路径
        
        Args:
            data_file_path: 数据文件路径
        
        Returns:
            元数据文件路径
        
        规则：
            /path/to/EC_GOODS_PHONE_20240108_0001.json
            -> /path/to/EC_GOODS_PHONE_20240108_0001.metadata.json
        """
        path = Path(data_file_path)
        stem = path.stem  # 不带扩展名的文件名
        parent = path.parent
        metadata_filename = f"{stem}.metadata.json"
        return str(parent / metadata_filename)
    
    @staticmethod
    def extract_business_type_id(metadata: Dict[str, Any]) -> Optional[str]:
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
    def extract_crawl_date(metadata: Dict[str, Any]) -> Optional[str]:
        """
        从元数据中提取抓取日期
        
        Args:
            metadata: 元数据字典
        
        Returns:
            抓取日期（YYYYMMDD格式）
        """
        return metadata.get('crawl_date')


def load_metadata(data_file_path: str) -> Optional[Dict[str, Any]]:
    """快速加载元数据"""
    return MetadataLoader.load_metadata(data_file_path)
