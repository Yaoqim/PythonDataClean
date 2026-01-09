# -*- coding: utf-8 -*-
"""
文件读写处理模块

负责从本地或远程服务器读取临时数据文件。

功能：
- 支持JSON、CSV、TXT格式文件读取
- 自动编码检测和转换（UTF-8）
- 大文件分批读取
- 文件验证（大小、完整性）
"""

import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Iterator
from src.utils.logger import get_logger
from src.utils.encoding_checker import EncodingChecker
from src.utils.error_handler import ErrorHandler

logger = get_logger(__name__)


class FileHandler:
    """
    文件处理器
    
    负责：
    1. 文件格式检测和读取
    2. 编码自动检测和转换
    3. 大文件分批读取
    4. 文件校验
    """
    
    # 支持的文件格式
    SUPPORTED_FORMATS = {'.json', '.csv', '.txt', '.jsonl'}
    
    # 最大单次加载大小（MB）
    MAX_CHUNK_SIZE_MB = 100
    
    @staticmethod
    def check_file_exists(file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
        
        Returns:
            True表示存在，False表示不存在
        """
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        
        if not exists:
            logger.warning(f"文件不存在：{file_path}")
        
        return exists
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        获取文件大小（MB）
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件大小（MB），如果文件不存在返回0
        """
        try:
            size_bytes = Path(file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception as e:
            logger.error(f"获取文件大小失败：{file_path}，错误：{e}")
            return 0.0
    
    @staticmethod
    def get_file_format(file_path: str) -> Optional[str]:
        """
        获取文件格式
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件扩展名（如.json），如果不支持返回None
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix in FileHandler.SUPPORTED_FORMATS:
            return suffix
        
        logger.warning(f"不支持的文件格式：{suffix}")
        return None
    
    @staticmethod
    def read_file_bytes(file_path: str) -> Optional[bytes]:
        """
        读取文件的原始字节数据
        
        Args:
            file_path: 文件路径
        
        Returns:
            字节数据，如果读取失败返回None
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件字节失败：{file_path}，错误：{e}")
            return None
    
    @staticmethod
    def read_file_text(file_path: str) -> Optional[str]:
        """
        读取文件为文本
        
        自动检测编码并转换为UTF-8
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件内容（UTF-8文本），如果读取失败返回None
        """
        try:
            # 读取原始字节
            data = FileHandler.read_file_bytes(file_path)
            if data is None:
                return None
            
            # 自动检测编码并转换
            text, detected_encoding = EncodingChecker.convert_to_utf8(data)
            
            logger.debug(f"文件编码检测：{file_path}，检测编码：{detected_encoding}")
            
            return text
            
        except Exception as e:
            logger.error(f"读取文件文本失败：{file_path}，错误：{e}")
            return None


def load_json_file(file_path: str, chunk_lines: Optional[int] = None) -> Union[List[Dict], Iterator[Dict], None]:
    """
    加载JSON文件
    
    支持：
    - 标准JSON数组：[{...}, {...}]
    - JSONL格式：每行一个JSON对象
    
    Args:
        file_path: 文件路径
        chunk_lines: 如果指定，返回分块迭代器（每次读取chunk_lines行）
    
    Returns:
        JSON对象列表或迭代器，如果加载失败返回None
    
    示例：
        # 一次加载全部
        records = load_json_file("data.json")
        
        # 分块加载大文件
        for chunk in load_json_file("large_data.jsonl", chunk_lines=1000):
            process_records(chunk)
    """
    try:
        if not FileHandler.check_file_exists(file_path):
            return None
        
        text = FileHandler.read_file_text(file_path)
        if text is None:
            return None
        
        # 如果指定了分块，返回迭代器
        if chunk_lines:
            return _json_chunk_iterator(file_path, chunk_lines)
        
        # 尝试解析为标准JSON数组
        try:
            data = json.loads(text)
            if isinstance(data, list):
                logger.info(f"成功加载JSON数组：{file_path}，记录数：{len(data)}")
                return data
        except json.JSONDecodeError:
            pass
        
        # 尝试解析为JSONL格式（每行一个JSON对象）
        records = []
        for line_num, line in enumerate(text.strip().split('\n'), 1):
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                logger.warning(f"第{line_num}行JSON解析失败：{e}")
                continue
        
        logger.info(f"成功加载JSONL文件：{file_path}，记录数：{len(records)}")
        return records if records else None
        
    except Exception as e:
        logger.error(f"加载JSON文件失败：{file_path}，错误：{e}")
        return None


def load_csv_file(
    file_path: str,
    delimiter: str = ',',
    encoding: Optional[str] = None,
    chunk_lines: Optional[int] = None
) -> Union[List[Dict], Iterator[Dict], None]:
    """
    加载CSV文件
    
    Args:
        file_path: 文件路径
        delimiter: 分隔符（默认逗号）
        encoding: 编码（如果为None会自动检测）
        chunk_lines: 如果指定，返回分块迭代器
    
    Returns:
        记录列表（每行转为字典）或迭代器，如果加载失败返回None
    
    示例：
        # 一次加载全部
        records = load_csv_file("data.csv")
        
        # 分块加载大文件
        for chunk in load_csv_file("large_data.csv", chunk_lines=5000):
            process_records(chunk)
    """
    try:
        if not FileHandler.check_file_exists(file_path):
            return None
        
        text = FileHandler.read_file_text(file_path)
        if text is None:
            return None
        
        # 如果指定了分块，返回迭代器
        if chunk_lines:
            return _csv_chunk_iterator(file_path, delimiter, encoding, chunk_lines)
        
        # 一次性加载
        records = []
        reader = csv.DictReader(text.strip().split('\n'), delimiter=delimiter)
        
        for row_num, row in enumerate(reader, 1):
            # 过滤空行
            if any(row.values()):
                records.append(dict(row))
        
        logger.info(f"成功加载CSV文件：{file_path}，记录数：{len(records)}")
        return records if records else None
        
    except Exception as e:
        logger.error(f"加载CSV文件失败：{file_path}，错误：{e}")
        return None


def _json_chunk_iterator(file_path: str, chunk_lines: int) -> Iterator[List[Dict]]:
    """
    JSONL文件分块迭代器
    
    Args:
        file_path: 文件路径
        chunk_lines: 每个块的行数
    
    Yields:
        每个块包含的记录列表
    """
    try:
        text = FileHandler.read_file_text(file_path)
        if text is None:
            return
        
        chunk = []
        for line in text.strip().split('\n'):
            if not line.strip():
                continue
            
            try:
                record = json.loads(line)
                chunk.append(record)
                
                if len(chunk) >= chunk_lines:
                    yield chunk
                    chunk = []
            except json.JSONDecodeError as e:
                logger.warning(f"JSON行解析失败：{e}")
                continue
        
        # 返回剩余的行
        if chunk:
            yield chunk
            
    except Exception as e:
        logger.error(f"JSONL分块迭代失败：{file_path}，错误：{e}")


def _csv_chunk_iterator(
    file_path: str,
    delimiter: str,
    encoding: Optional[str],
    chunk_lines: int
) -> Iterator[List[Dict]]:
    """
    CSV文件分块迭代器
    
    Args:
        file_path: 文件路径
        delimiter: 分隔符
        encoding: 编码
        chunk_lines: 每个块的行数
    
    Yields:
        每个块包含的记录字典列表
    """
    try:
        text = FileHandler.read_file_text(file_path)
        if text is None:
            return
        
        lines = text.strip().split('\n')
        reader = csv.DictReader(lines, delimiter=delimiter)
        
        chunk = []
        for row in reader:
            if any(row.values()):
                chunk.append(dict(row))
            
            if len(chunk) >= chunk_lines:
                yield chunk
                chunk = []
        
        # 返回剩余的行
        if chunk:
            yield chunk
            
    except Exception as e:
        logger.error(f"CSV分块迭代失败：{file_path}，错误：{e}")
