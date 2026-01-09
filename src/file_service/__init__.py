# -*- coding: utf-8 -*-
"""
文件操作模块

负责从阿里云服务器获取、读写、验证临时数据文件。
"""

from src.file_service.file_handler import FileHandler, read_json_file, read_csv_file
from src.file_service.metadata_loader import MetadataLoader, load_metadata

__all__ = [
    "FileHandler",
    "read_json_file",
    "read_csv_file",
    "MetadataLoader",
    "load_metadata",
]
