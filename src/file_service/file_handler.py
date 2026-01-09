# -*- coding: utf-8 -*-
"""
文件读写处理模块

支持多种文件格式：JSON、CSV、JSONL、Parquet等
实现UTF-8编码检查和转换
"""

import json
import csv
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger
from src.utils.encoding_checker import convert_to_utf8
from src.utils.error_handler import ErrorHandler

logger = get_logger(__name__)


class FileHandler:
    """
    文件处理器
    
    负责：
    1. 读取各种格式的数据文件
    2. 验证文件编码
    3. 处理文件错误
    """
    
    SUPPORTED_FORMATS = ["json", "csv", "jsonl", "parquet", "xml", "txt"]
    
    @staticmethod
    def read_file(file_path: str, file_format: Optional[str] = None) -> Union[List[Dict[str, Any]], pd.DataFrame, None]:
        """
        通用文件读取接口
        
        Args:
            file_path: 文件路径
            file_format: 文件格式（自动检测如果为None）
        
        Returns:
            读取的数据（格式取决于文件类型）
        """
        file_path = str(file_path)
        
        # 检查文件存在性
        if not os.path.exists(file_path):
            logger.error(f"文件不存在：{file_path}")
            ErrorHandler.handle_file_read_error(file_path, FileNotFoundError("文件不存在"))
            return None
        
        # 自动检测格式
        if file_format is None:
            file_format = os.path.splitext(file_path)[1].lstrip('.').lower()
        
        try:
            if file_format == "json":
                return FileHandler.read_json_file(file_path)
            elif file_format == "csv":
                return FileHandler.read_csv_file(file_path)
            elif file_format == "jsonl":
                return FileHandler.read_jsonl_file(file_path)
            elif file_format == "parquet":
                return FileHandler.read_parquet_file(file_path)
            else:
                logger.error(f"不支持的文件格式：{file_format}")
                return None
        
        except Exception as e:
            ErrorHandler.handle_file_read_error(file_path, e)
            return None
    
    @staticmethod
    def read_json_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        读取JSON文件
        
        Args:
            file_path: JSON文件路径
        
        Returns:
            解析后的数据（列表或字典）
        """
        try:
            with open(file_path, 'rb') as f:
                data_bytes = f.read()
            
            # 检查编码
            text, encoding = convert_to_utf8(data_bytes)
            logger.debug(f"JSON文件编码：{encoding}")
            
            # 解析JSON
            data = json.loads(text)
            
            # 如果是单个对象，转为列表
            if isinstance(data, dict):
                data = [data]
            
            logger.info(f"成功读取JSON文件：{file_path}，记录数：{len(data) if isinstance(data, list) else 1}")
            return data if isinstance(data, list) else [data]
            
        except Exception as e:
            logger.error(f"JSON文件读取失败：{file_path}，错误：{e}")
            raise
    
    @staticmethod
    def read_csv_file(
        file_path: str,
        encoding: str = 'utf-8',
        delimiter: str = ','
    ) -> Optional[List[Dict[str, Any]]]:
        """
        读取CSV文件
        
        Args:
            file_path: CSV文件路径
            encoding: 文件编码
            delimiter: 分隔符
        
        Returns:
            记录列表
        """
        try:
            # 首先尝试读取字节并检测编码
            with open(file_path, 'rb') as f:
                first_bytes = f.read(1024)
            
            text, detected_encoding = convert_to_utf8(first_bytes)
            actual_encoding = detected_encoding if detected_encoding else encoding
            
            logger.debug(f"CSV文件编码：{actual_encoding}")
            
            # 使用pandas读取CSV
            df = pd.read_csv(
                file_path,
                encoding=actual_encoding,
                delimiter=delimiter,
                keep_default_na=False
            )
            
            # 转为字典列表
            records = df.to_dict('records')
            logger.info(f"成功读取CSV文件：{file_path}，记录数：{len(records)}")
            return records
            
        except Exception as e:
            logger.error(f"CSV文件读取失败：{file_path}，错误：{e}")
            raise
    
    @staticmethod
    def read_jsonl_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        读取JSONL文件（行式JSON）
        
        Args:
            file_path: JSONL文件路径
        
        Returns:
            记录列表
        """
        records = []
        try:
            with open(file_path, 'rb') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    try:
                        # 检查编码
                        text, _ = convert_to_utf8(line)
                        record = json.loads(text)
                        records.append(record)
                    except json.JSONDecodeError as e:
                        logger.warning(f"第{line_num}行JSON解析失败：{e}")
                        continue
            
            logger.info(f"成功读取JSONL文件：{file_path}，记录数：{len(records)}")
            return records
            
        except Exception as e:
            logger.error(f"JSONL文件读取失败：{file_path}，错误：{e}")
            raise
    
    @staticmethod
    def read_parquet_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        读取Parquet文件
        
        Args:
            file_path: Parquet文件路径
        
        Returns:
            记录列表
        """
        try:
            df = pd.read_parquet(file_path)
            records = df.to_dict('records')
            logger.info(f"成功读取Parquet文件：{file_path}，记录数：{len(records)}")
            return records
            
        except Exception as e:
            logger.error(f"Parquet文件读取失败：{file_path}，错误：{e}")
            raise


# 便利函数
def read_json_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """快速读取JSON文件"""
    return FileHandler.read_json_file(file_path)


def read_csv_file(file_path: str, delimiter: str = ',') -> Optional[List[Dict[str, Any]]]:
    """快速读取CSV文件"""
    return FileHandler.read_csv_file(file_path, delimiter=delimiter)
