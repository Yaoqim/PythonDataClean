# -*- coding: utf-8 -*-
"""
文件操作服务模块

提供文件读取、元数据加载等功能，是数据清洗流程的第一步。

模块功能：
1. file_handler.py - 文件读写操作
2. metadata_loader.py - 元数据加载与验证
"""

from src.file_service.file_handler import FileHandler, load_json_file, load_csv_file
from src.file_service.metadata_loader import MetadataLoader, load_metadata

__all__ = [
    "FileHandler",
    "load_json_file",
    "load_csv_file",
    "MetadataLoader",
    "load_metadata",
]
