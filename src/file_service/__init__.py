# -*- coding: utf-8 -*-
"""
文件操作服务模块

提供文件读取、元数据加载等功能，是数据清洗流程的第一步。

模块功能：
1. file_handler.py - 文件读写操作（支持本地和OSS）
2. aliyun_client.py - 阿里云OSS服务客户端
3. file_validator.py - 文件验证（编码、格式、完整性）
4. file_utils.py - 文件工具函数
5. metadata_loader.py - 元数据加载与验证
"""

from src.file_service.file_handler import FileHandler, load_json_file, load_csv_file
from src.file_service.aliyun_client import AliyunOSSClient
from src.file_service.file_validator import FileValidator
from src.file_service.file_utils import FileUtils
from src.file_service.metadata_loader import MetadataLoader, load_metadata

__all__ = [
    "FileHandler",
    "load_json_file",
    "load_csv_file",
    "AliyunOSSClient",
    "FileValidator",
    "FileUtils",
    "MetadataLoader",
    "load_metadata",
]
