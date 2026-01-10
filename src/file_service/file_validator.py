# -*- coding: utf-8 -*-
"""
文件验证器

负责：
- 编码检查（确保UTF-8，预防乱码）
- 格式验证
- 文件大小验证
- 完整性校验
"""

import hashlib
from pathlib import Path
from typing import Optional, Tuple

from src.utils.logger import get_logger
from src.utils.encoding_checker import EncodingChecker
from src.file_service.file_handler import FileHandler

logger = get_logger(__name__)


class FileValidator:
    """文件验证器"""
    
    # 最大文件大小（MB）
    MAX_FILE_SIZE_MB = 500
    
    # 支持的格式
    SUPPORTED_FORMATS = {'.json', '.csv', '.txt', '.jsonl'}
    
    @staticmethod
    def check_file_encoding(file_path: str) -> Tuple[bool, str]:
        """
        检查文件编码是否为UTF-8
        
        Args:
            file_path: 文件路径
        
        Returns:
            (是否为UTF-8, 检测到的编码)
        """
        try:
            data = FileHandler.read_file_bytes(file_path)
            if data is None:
                return False, "unknown"
            
            # 检测编码
            detected_encoding = EncodingChecker.detect_encoding(data)
            
            # 尝试转换为UTF-8
            try:
                text, _ = EncodingChecker.convert_to_utf8(data)
                if text is None:
                    return False, detected_encoding
                
                logger.info(f"文件编码检查通过：{file_path}，编码：{detected_encoding}")
                return True, detected_encoding
            
            except Exception as e:
                logger.warning(f"编码转换失败：{file_path}，错误：{e}")
                return False, detected_encoding
        
        except Exception as e:
            logger.error(f"编码检查失败：{file_path}，错误：{e}")
            return False, "error"
    
    @staticmethod
    def validate_format(file_path: str, expected_format: Optional[str] = None) -> bool:
        """
        验证文件格式
        
        Args:
            file_path: 文件路径
            expected_format: 期望的格式（如'.json'），如果为None则只检查支持的格式
        
        Returns:
            格式是否有效
        """
        try:
            file_format = FileHandler.get_file_format(file_path)
            
            if file_format is None:
                logger.warning(f"不支持的文件格式：{file_path}")
                return False
            
            if expected_format and file_format != expected_format.lower():
                logger.warning(f"文件格式不匹配：{file_path}，期望：{expected_format}，实际：{file_format}")
                return False
            
            logger.info(f"文件格式验证通过：{file_path}，格式：{file_format}")
            return True
        
        except Exception as e:
            logger.error(f"文件格式验证失败：{file_path}，错误：{e}")
            return False
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: Optional[float] = None) -> Tuple[bool, float]:
        """
        验证文件大小
        
        Args:
            file_path: 文件路径
            max_size_mb: 最大允许大小（MB），默认为系统配置
        
        Returns:
            (大小是否有效, 文件大小MB)
        """
        try:
            max_size = max_size_mb if max_size_mb else FileValidator.MAX_FILE_SIZE_MB
            file_size = FileHandler.get_file_size_mb(file_path)
            
            if file_size > max_size:
                logger.warning(f"文件过大：{file_path}，大小：{file_size}MB，最大允许：{max_size}MB")
                return False, file_size
            
            logger.info(f"文件大小验证通过：{file_path}，大小：{file_size}MB")
            return True, file_size
        
        except Exception as e:
            logger.error(f"文件大小验证失败：{file_path}，错误：{e}")
            return False, 0.0
    
    @staticmethod
    def calculate_checksum(file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """
        计算文件校验和
        
        Args:
            file_path: 文件路径
            algorithm: 算法（'md5' 或 'sha256'）
        
        Returns:
            校验和字符串
        """
        try:
            if algorithm == 'md5':
                hasher = hashlib.md5()
            elif algorithm == 'sha256':
                hasher = hashlib.sha256()
            else:
                logger.error(f"不支持的算法：{algorithm}")
                return None
            
            data = FileHandler.read_file_bytes(file_path)
            if data is None:
                return None
            
            hasher.update(data)
            checksum = hasher.hexdigest()
            
            logger.info(f"文件校验和计算完成：{file_path}，{algorithm}：{checksum}")
            return checksum
        
        except Exception as e:
            logger.error(f"校验和计算失败：{file_path}，错误：{e}")
            return None
    
    @staticmethod
    def verify_checksum(file_path: str, expected_checksum: str, algorithm: str = 'md5') -> bool:
        """
        验证文件完整性
        
        Args:
            file_path: 文件路径
            expected_checksum: 期望的校验和
            algorithm: 算法
        
        Returns:
            校验和是否匹配
        """
        try:
            actual_checksum = FileValidator.calculate_checksum(file_path, algorithm)
            
            if actual_checksum is None:
                return False
            
            if actual_checksum.lower() != expected_checksum.lower():
                logger.warning(f"校验和不匹配：{file_path}，期望：{expected_checksum}，实际：{actual_checksum}")
                return False
            
            logger.info(f"文件完整性验证通过：{file_path}")
            return True
        
        except Exception as e:
            logger.error(f"校验和验证失败：{file_path}，错误：{e}")
            return False
    
    @staticmethod
    def validate_file(file_path: str, expected_format: Optional[str] = None) -> Tuple[bool, dict]:
        """
        执行完整的文件验证
        
        Args:
            file_path: 文件路径
            expected_format: 期望的格式
        
        Returns:
            (验证是否通过, 验证详情)
        """
        results = {
            'file_path': file_path,
            'encoding_valid': False,
            'format_valid': False,
            'size_valid': False,
            'encoding': 'unknown',
            'file_size_mb': 0.0,
            'errors': []
        }
        
        try:
            # 检查编码
            encoding_valid, detected_encoding = FileValidator.check_file_encoding(file_path)
            results['encoding_valid'] = encoding_valid
            results['encoding'] = detected_encoding
            
            if not encoding_valid:
                results['errors'].append(f"编码检查失败，检测到的编码：{detected_encoding}")
            
            # 检查格式
            format_valid = FileValidator.validate_format(file_path, expected_format)
            results['format_valid'] = format_valid
            
            if not format_valid:
                results['errors'].append(f"格式检查失败")
            
            # 检查大小
            size_valid, file_size = FileValidator.validate_file_size(file_path)
            results['size_valid'] = size_valid
            results['file_size_mb'] = file_size
            
            if not size_valid:
                results['errors'].append(f"文件过大：{file_size}MB")
            
            # 综合判断
            passed = encoding_valid and format_valid and size_valid
            
            if passed:
                logger.info(f"文件验证完全通过：{file_path}")
            else:
                logger.warning(f"文件验证失败：{file_path}，错误数：{len(results['errors'])}")
            
            return passed, results
        
        except Exception as e:
            logger.error(f"文件验证异常：{file_path}，错误：{e}")
            results['errors'].append(str(e))
            return False, results
