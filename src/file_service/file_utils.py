# -*- coding: utf-8 -*-
"""
文件工具函数

负责：
- 路径处理和规范化
- 文件命名规范检查
- OSS路径和本地路径转换
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class FileUtils:
    """文件工具类"""
    
    # 文件命名规则：{业务类型}_{日期}_{序号}.{扩展名}
    # 例如：EC_GOODS_PHONE_20240108_0001.json
    FILE_NAME_PATTERN = r'^([A-Z_]+)_(\d{8})_(\d{4})\.(json|csv|txt|jsonl)$'
    
    # 元数据文件后缀
    METADATA_SUFFIX = '.metadata.json'
    
    @staticmethod
    def is_oss_path(file_path: str) -> bool:
        """
        判断是否为OSS路径
        
        Args:
            file_path: 文件路径
        
        Returns:
            True表示OSS路径，False表示本地路径
        """
        return file_path.startswith('oss://') or file_path.startswith('/aliyun/')
    
    @staticmethod
    def normalize_oss_path(oss_path: str) -> str:
        """
        规范化OSS路径
        
        将 oss://bucket/path 转换为 /path
        将 /aliyun/path 保持原样
        
        Args:
            oss_path: OSS路径
        
        Returns:
            规范化后的路径
        """
        if oss_path.startswith('oss://'):
            # oss://bucket/path -> /path
            parts = oss_path.split('/', 3)
            if len(parts) >= 4:
                return '/' + parts[3]
            return '/'
        
        # /aliyun/path 已经是标准格式
        return oss_path
    
    @staticmethod
    def normalize_local_path(local_path: str) -> str:
        """
        规范化本地路径
        
        Args:
            local_path: 本地路径
        
        Returns:
            规范化后的绝对路径
        """
        return os.path.abspath(local_path)
    
    @staticmethod
    def validate_file_name(file_name: str) -> Tuple[bool, Optional[dict]]:
        """
        验证文件名是否符合规范
        
        规范：{业务类型}_{日期}_{序号}.{扩展名}
        示例：EC_GOODS_PHONE_20240108_0001.json
        
        Args:
            file_name: 文件名
        
        Returns:
            (是否符合规范, 解析结果)
        """
        match = re.match(FileUtils.FILE_NAME_PATTERN, file_name)
        
        if not match:
            logger.warning(f"文件名不符合规范：{file_name}")
            return False, None
        
        business_type, crawl_date, sequence, extension = match.groups()
        
        # 验证日期格式
        try:
            from datetime import datetime
            datetime.strptime(crawl_date, '%Y%m%d')
        except ValueError:
            logger.warning(f"日期格式无效：{crawl_date}")
            return False, None
        
        result = {
            'file_name': file_name,
            'business_type': business_type,
            'crawl_date': crawl_date,
            'sequence': sequence,
            'extension': extension
        }
        
        logger.info(f"文件名验证通过：{file_name}，业务类型：{business_type}")
        return True, result
    
    @staticmethod
    def get_metadata_file_path(data_file_path: str) -> str:
        """
        获取对应的元数据文件路径
        
        将 file.json 转换为 file.metadata.json
        
        Args:
            data_file_path: 数据文件路径
        
        Returns:
            元数据文件路径
        """
        if data_file_path.endswith(FileUtils.METADATA_SUFFIX):
            return data_file_path
        
        # 移除原文件扩展名，添加.metadata.json
        base_path = os.path.splitext(data_file_path)[0]
        metadata_path = base_path + FileUtils.METADATA_SUFFIX
        
        return metadata_path
    
    @staticmethod
    def extract_business_type_from_path(file_path: str) -> Optional[str]:
        """
        从文件路径提取业务类型
        
        Args:
            file_path: 文件路径
        
        Returns:
            业务类型ID，如果无法提取返回None
        """
        try:
            # 获取文件名
            file_name = Path(file_path).name
            
            # 移除元数据后缀
            if file_name.endswith(FileUtils.METADATA_SUFFIX):
                file_name = file_name.replace(FileUtils.METADATA_SUFFIX, '.json')
            
            # 验证文件名
            valid, parsed = FileUtils.validate_file_name(file_name)
            
            if valid and parsed:
                return parsed['business_type']
            
            return None
        
        except Exception as e:
            logger.error(f"提取业务类型失败：{file_path}，错误：{e}")
            return None
    
    @staticmethod
    def extract_crawl_date_from_path(file_path: str) -> Optional[str]:
        """
        从文件路径提取抓取日期
        
        Args:
            file_path: 文件路径
        
        Returns:
            抓取日期（YYYYMMDD格式），如果无法提取返回None
        """
        try:
            file_name = Path(file_path).name
            
            if file_name.endswith(FileUtils.METADATA_SUFFIX):
                file_name = file_name.replace(FileUtils.METADATA_SUFFIX, '.json')
            
            valid, parsed = FileUtils.validate_file_name(file_name)
            
            if valid and parsed:
                return parsed['crawl_date']
            
            return None
        
        except Exception as e:
            logger.error(f"提取抓取日期失败：{file_path}，错误：{e}")
            return None
    
    @staticmethod
    def get_local_temp_path(data_file_path: str) -> str:
        """
        获取本地临时缓存路径
        
        Args:
            data_file_path: 数据文件路径（可能是OSS或本地）
        
        Returns:
            本地临时缓存路径
        """
        import tempfile
        
        # 获取文件名
        file_name = Path(data_file_path).name
        
        # 在临时目录创建缓存
        temp_dir = os.path.join(tempfile.gettempdir(), 'pydataclean')
        os.makedirs(temp_dir, exist_ok=True)
        
        return os.path.join(temp_dir, file_name)
    
    @staticmethod
    def build_oss_path(business_type: str, crawl_date: str, sequence: str, extension: str = 'json') -> str:
        """
        构建标准OSS路径
        
        Args:
            business_type: 业务类型
            crawl_date: 抓取日期（YYYYMMDD）
            sequence: 序列号（0001等）
            extension: 文件扩展名
        
        Returns:
            标准OSS路径
        """
        file_name = f"{business_type}_{crawl_date}_{sequence}.{extension}"
        oss_path = f"/{business_type}/{crawl_date}/{file_name}"
        return oss_path
    
    @staticmethod
    def compare_paths(path1: str, path2: str) -> bool:
        """
        比较两个路径是否指向同一个文件
        
        支持OSS和本地路径混合比较
        
        Args:
            path1: 路径1
            path2: 路径2
        
        Returns:
            是否指向同一文件
        """
        # 规范化路径
        if FileUtils.is_oss_path(path1):
            normalized1 = FileUtils.normalize_oss_path(path1)
        else:
            normalized1 = FileUtils.normalize_local_path(path1)
        
        if FileUtils.is_oss_path(path2):
            normalized2 = FileUtils.normalize_oss_path(path2)
        else:
            normalized2 = FileUtils.normalize_local_path(path2)
        
        return normalized1 == normalized2
