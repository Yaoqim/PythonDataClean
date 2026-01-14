# -*- coding: utf-8 -*-
"""
文件读写处理模块

负责从本地或远程服务器读取临时数据文件。

功能：
- 支持JSON、CSV、TXT格式文件读取
- 自动编码检测和转换（UTF-8）
- 大文件分批读取
- 文件验证（大小、完整性）
- 支持从阿里云OSS获取文件
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
    SUPPORTED_FORMATS = {'.json', '.csv', '.txt', '.jsonl', '.xlsx', '.xls'}
    
    # 最大单次加载大小（MB）
    MAX_CHUNK_SIZE_MB = 50  # 降低阈值，建议大文件分批处理
    
    @staticmethod
    def check_file_exists(file_path: str) -> bool:
        """
        检查文件是否存在
        
        支持本地文件和OSS文件
        
        Args:
            file_path: 文件路径（本地或OSS）
        
        Returns:
            True表示存在，False表示不存在
        """
        # 处理OSS文件
        if file_path.startswith('oss://') or file_path.startswith('/aliyun/'):
            try:
                from src.file_service.aliyun_client import AliyunOSSClient
                oss_client = AliyunOSSClient()
                
                # 规范化OSS路径
                if file_path.startswith('oss://'):
                    # oss://bucket/path -> path (不加前缀/)
                    oss_path = file_path.split('/', 3)[-1]
                else:
                    # /aliyun/path -> path
                    oss_path = file_path.replace('/aliyun/', '')
                
                exists = oss_client.file_exists(oss_path)
                if not exists:
                    logger.warning(f"OSS文件不存在：{file_path}")
                return exists
            except Exception as e:
                logger.error(f"检查OSS文件存在性失败：{file_path}，错误：{e}")
                return False
        
        # 处理本地文件
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        
        if not exists:
            logger.warning(f"文件不存在：{file_path}")
        
        return exists
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        获取文件大小（MB）
        """
        try:
            # 处理OSS路径
            if file_path.startswith(('oss://', '/aliyun/')):
                # 这里简单处理：如果元数据中有大小则由编排器处理，此处返回0以防报错
                return 0.0
                
            size_bytes = Path(file_path).stat().st_size
            return size_bytes / (1024 * 1024)
        except Exception as e:
            logger.error(f"获取文件大小失败：{file_path}，错误：{e}")
            return 0.0

    @staticmethod
    def get_file_hash(file_path: str) -> str:
        """计算本地文件的MD5指纹"""
        import hashlib
        if not os.path.exists(file_path):
            return ""
        
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件Hash失败：{file_path}，错误：{e}")
            return ""
    
    @staticmethod
    def get_file_format(file_path: str) -> Optional[str]:
        """
        获取文件格式
        
        支持本地文件和OSS文件路径
        
        Args:
            file_path: 文件路径（本地或OSS）
        
        Returns:
            文件扩展名（如.json），如果不支持返回None
        """
        # 处理OSS路径 (oss://bucket/path/file.json 或 /aliyun/path/file.json)
        if file_path.startswith('oss://') or file_path.startswith('/aliyun/'):
            return FileHandler._get_oss_file_format(file_path)
        
        # 处理本地路径
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix in FileHandler.SUPPORTED_FORMATS:
            return suffix
        
        logger.warning(f"不支持的文件格式：{suffix}")
        return None
    
    @staticmethod
    def _get_oss_file_format(oss_path: str) -> Optional[str]:
        """
        从OSS路径获取文件格式
        
        Args:
            oss_path: OSS文件路径
        
        Returns:
            文件扩展名
        """
        # 处理oss://bucket/path或/aliyun/path格式
        if oss_path.startswith('oss://'):
            path_part = oss_path.split('/', 3)[-1] if '/' in oss_path else oss_path
        else:
            path_part = oss_path
        
        suffix = Path(path_part).suffix.lower()
        
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
        支持本地和OSS文件
        
        Args:
            file_path: 文件路径（本地或OSS）
        
        Returns:
            文件内容（UTF-8文本），如果读取失败返回None
        """
        try:
            is_temp = False
            # 如果是OSS文件，先下载到本地
            if file_path.startswith('oss://') or file_path.startswith('/aliyun/'):
                from src.file_service.aliyun_client import AliyunOSSClient
                logger.info(f"从OSS读取文件：{file_path}")
                oss_client = AliyunOSSClient()
                
                # 规范化OSS路径
                if file_path.startswith('oss://'):
                    # oss://bucket/path -> path (不加前缀/)
                    oss_path = file_path.split('/', 3)[-1]
                else:
                    # /aliyun/path -> path
                    oss_path = file_path.replace('/aliyun/', '')
                
                local_path = oss_client.get_file_to_temp(oss_path)
                if not local_path:
                    logger.error(f"从OSS下载文件失败：{file_path}")
                    return None
                
                file_path = local_path
                is_temp = True
            
            # 读取原始字节
            data = FileHandler.read_file_bytes(file_path)
            if data is None:
                return None
            
            # 自动检测编码并转换
            text, detected_encoding = EncodingChecker.convert_to_utf8(data)
            logger.debug(f"文件编码检测：{file_path}，检测编码：{detected_encoding}")
            
            # 如果是临时文件，读取后立即删除
            if is_temp and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"已删除OSS临时文件：{file_path}")
                
            return text
            
        except Exception as e:
            logger.error(f"读取文件文本失败：{file_path}，错误：{e}")
            return None


def load_json_file(file_path: str, chunk_lines: Optional[int] = None) -> Union[List[Dict], Iterator[List[Dict]], None]:
    """
    加载JSON文件，支持本地和OSS路径
    """
    is_temp = False
    local_path = file_path
    try:
        from src.file_service.aliyun_client import AliyunOSSClient
        import os
        
        if file_path.startswith(('oss://', '/aliyun/')):
            oss_client = AliyunOSSClient()
            if file_path.startswith('oss://'):
                oss_path = file_path.split('/', 3)[-1]
            else:
                oss_path = file_path.replace('/aliyun/', '')
            
            local_path = oss_client.get_file_to_temp(oss_path)
            if not local_path:
                return None
            is_temp = True
            
        if chunk_lines:
            return _json_chunk_iterator(local_path, chunk_lines, is_temp)
        
        text = FileHandler.read_file_text(local_path)
        if text is None:
            return None
        
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
    finally:
        if not chunk_lines and is_temp and os.path.exists(local_path):
            os.remove(local_path)
            logger.debug(f"已删除JSON临时文件：{local_path}")


def load_csv_file(
    file_path: str,
    delimiter: str = ',',
    encoding: Optional[str] = None,
    chunk_lines: Optional[int] = None
) -> Union[List[Dict], Iterator[List[Dict]], None]:
    """
    加载CSV文件，支持本地和OSS路径
    """
    is_temp = False
    local_path = file_path
    try:
        from src.file_service.aliyun_client import AliyunOSSClient
        import os
        
        if file_path.startswith(('oss://', '/aliyun/')):
            oss_client = AliyunOSSClient()
            if file_path.startswith('oss://'):
                oss_path = file_path.split('/', 3)[-1]
            else:
                oss_path = file_path.replace('/aliyun/', '')
            
            local_path = oss_client.get_file_to_temp(oss_path)
            if not local_path: return None
            is_temp = True
            
        if chunk_lines:
            return _csv_chunk_iterator(local_path, delimiter, encoding, chunk_lines, is_temp)
        
        text = FileHandler.read_file_text(local_path)
        if text is None: return None
        
        records = []
        import csv
        import io
        reader = csv.DictReader(io.StringIO(text.strip()), delimiter=delimiter)
        for row in reader:
            if any(row.values()):
                records.append(dict(row))
        
        logger.info(f"成功加载CSV文件：{file_path}，记录数：{len(records)}")
        return records
    finally:
        if not chunk_lines and is_temp and os.path.exists(local_path):
            os.remove(local_path)
            logger.debug(f"已删除CSV临时文件：{local_path}")

def _csv_chunk_iterator(file_path: str, delimiter: str, encoding: Optional[str], chunk_lines: int, is_temp: bool = False) -> Iterator[List[Dict]]:
    """CSV文件分块迭代器"""
    try:
        import pandas as pd
        # 使用 pandas 优化大 CSV 读取
        reader = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding or 'utf-8', chunksize=chunk_lines)
        for df in reader:
            df = df.where(df.notnull(), None)
            yield df.to_dict('records')
    except Exception as e:
        logger.error(f"CSV分块迭代失败，错误：{e}")
    finally:
        if is_temp and os.path.exists(file_path):
            import os
            os.remove(file_path)
            logger.debug(f"已删除CSV分块临时文件：{file_path}")


def load_excel_file(file_path: str, chunk_size: Optional[int] = None) -> Union[List[Dict], Iterator[List[Dict]], None]:
    """
    加载Excel文件 (.xlsx, .xls)
    
    支持本地路径和OSS路径
    """
    is_temp = False
    local_path = file_path
    try:
        from src.file_service.aliyun_client import AliyunOSSClient
        import pandas as pd
        import os
        
        # 处理OSS文件
        if file_path.startswith(('oss://', '/aliyun/')):
            logger.info(f"从OSS下载Excel文件：{file_path}")
            oss_client = AliyunOSSClient()
            if file_path.startswith('oss://'):
                oss_path = file_path.split('/', 3)[-1]
            else:
                oss_path = file_path.replace('/aliyun/', '')
            
            local_path = oss_client.get_file_to_temp(oss_path)
            if not local_path:
                return None
            is_temp = True
            
        if chunk_size:
            # 使用 pandas 的 chunksize 参数
            reader = pd.read_excel(local_path, chunksize=chunk_size)
            return _excel_chunk_iterator(reader, local_path if is_temp else None)
        
        # 一次性加载
        df = pd.read_excel(local_path)
        # 将 NaN 转换为 None 方便后续处理
        df = df.where(pd.notnull(df), None)
        records = df.to_dict('records')
        
        logger.info(f"成功加载Excel文件：{file_path}，记录数：{len(records)}")
        return records
        
    except Exception as e:
        logger.error(f"加载Excel文件失败：{file_path}，错误：{e}")
        return None
    finally:
        # 如果不是分块模式且是临时文件，在此删除
        if not chunk_size and is_temp and os.path.exists(local_path):
            os.remove(local_path)
            logger.debug(f"已删除Excel临时文件：{local_path}")


def _excel_chunk_iterator(reader: Iterator, temp_path: Optional[str] = None) -> Iterator[List[Dict]]:
    """Excel文件分块迭代器"""
    try:
        for df in reader:
            df = df.where(df.notnull(), None)
            yield df.to_dict('records')
    except Exception as e:
        logger.error(f"Excel分块迭代失败，错误：{e}")
    finally:
        # 迭代结束或异常时，清理临时文件
        if temp_path and os.path.exists(temp_path):
            import os
            os.remove(temp_path)
            logger.debug(f"已删除Excel分块临时文件：{temp_path}")


def _json_chunk_iterator(file_path: str, chunk_lines: int, is_temp: bool = False) -> Iterator[List[Dict]]:
    """
    JSONL文件分块迭代器 - 优化大文件读取
    """
    try:
        import os
        with open(file_path, 'r', encoding='utf-8') as f:
            chunk = []
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    chunk.append(record)
                    
                    if len(chunk) >= chunk_lines:
                        yield chunk
                        chunk = []
                except Exception as e:
                    logger.warning(f"JSON行解析失败：{e}")
                    continue
            
            # 返回剩余的行
            if chunk:
                yield chunk
    finally:
        if is_temp and os.path.exists(file_path):
            import os
            os.remove(file_path)
            logger.debug(f"已删除JSON分块临时文件：{file_path}")


