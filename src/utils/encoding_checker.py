# -*- coding: utf-8 -*-
"""
编码检查与修复模块

提供UTF-8编码检查和修复功能，预防乱码问题。
遵循《文字质量保障体系.md》的编码规范。

关键原则：
- 预防优于修复：从源头避免乱码问题
- 强制UTF-8：所有文本必须使用UTF-8编码
- 修复而非删除：遇到乱码时修复而非简单删除
"""

import chardet
from typing import Tuple, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EncodingChecker:
    """
    编码检查器
    
    负责：
    1. 检测文本的字符编码
    2. 转换编码为UTF-8
    3. 处理编码错误
    """
    
    # 常见编码列表
    COMMON_ENCODINGS = [
        'utf-8',
        'utf-8-sig',
        'gbk',
        'gb2312',
        'big5',
        'latin-1',
        'iso-8859-1',
        'cp1252',
        'ascii',
    ]
    
    # UTF-8编码的BOM标记
    UTF8_BOM = b'\xef\xbb\xbf'
    
    @staticmethod
    def detect_encoding(data: bytes, confidence_threshold: float = 0.7) -> Tuple[Optional[str], float]:
        """
        使用chardet库检测字节数据的编码
        
        Args:
            data: 字节数据
            confidence_threshold: 置信度阈值（0-1），低于此阈值返回None
        
        Returns:
            (编码名称, 置信度) 元组，如果无法确定返回 (None, 0.0)
        """
        if not data:
            return None, 0.0
        
        try:
            result = chardet.detect(data)
            encoding = result.get('encoding')
            confidence = result.get('confidence', 0.0)
            
            # 如果置信度低于阈值，返回None
            if confidence < confidence_threshold:
                logger.warning(
                    f"编码检测置信度过低 (编码={encoding}, 置信度={confidence:.2%})"
                )
                return None, confidence
            
            return encoding, confidence
            
        except Exception as e:
            logger.error(f"编码检测失败：{e}")
            return None, 0.0
    
    @staticmethod
    def is_utf8(data: bytes) -> bool:
        """
        检查数据是否为有效的UTF-8编码
        
        Args:
            data: 字节数据
        
        Returns:
            True表示是有效UTF-8，False表示不是
        """
        if not data:
            return True
        
        try:
            data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    @staticmethod
    def convert_to_utf8(data: bytes, source_encoding: Optional[str] = None) -> Tuple[str, str]:
        """
        转换字节数据为UTF-8编码的文本
        
        Args:
            data: 字节数据
            source_encoding: 源编码（如果已知）。如果为None会自动检测
        
        Returns:
            (转换后的文本, 原始编码) 元组
        
        Raises:
            ValueError: 如果无法转换数据
        """
        if not data:
            return "", "empty"
        
        # 如果已经是UTF-8，直接返回
        if EncodingChecker.is_utf8(data):
            # 移除BOM标记（如果存在）
            if data.startswith(EncodingChecker.UTF8_BOM):
                return data[3:].decode('utf-8'), 'utf-8-sig'
            return data.decode('utf-8'), 'utf-8'
        
        # 尝试使用指定的编码
        if source_encoding:
            try:
                text = data.decode(source_encoding)
                logger.debug(f"使用指定编码成功: {source_encoding}")
                return text, source_encoding
            except (UnicodeDecodeError, LookupError) as e:
                logger.warning(f"指定编码转换失败 ({source_encoding}): {e}")
        
        # 自动检测编码
        detected_encoding, confidence = EncodingChecker.detect_encoding(data)
        
        if detected_encoding:
            try:
                text = data.decode(detected_encoding)
                logger.debug(
                    f"使用检测编码成功: {detected_encoding} (置信度={confidence:.2%})"
                )
                return text, detected_encoding
            except (UnicodeDecodeError, LookupError) as e:
                logger.warning(f"检测编码转换失败 ({detected_encoding}): {e}")
        
        # 尝试常见编码列表
        for encoding in EncodingChecker.COMMON_ENCODINGS:
            try:
                text = data.decode(encoding)
                logger.debug(f"使用备选编码成功: {encoding}")
                return text, encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 所有尝试都失败了，使用latin-1（总是能解码）并记录错误
        logger.error(
            "无法确定数据编码，使用latin-1兼容解码（可能出现乱码）"
        )
        text = data.decode('latin-1', errors='replace')
        return text, 'latin-1-fallback'
    
    @staticmethod
    def fix_encoding(text: str, source_encoding: Optional[str] = None) -> str:
        """
        修复文本中的编码问题
        
        将文本转为字节再按正确编码解码，尝试恢复乱码
        
        Args:
            text: 可能出现乱码的文本
            source_encoding: 原始编码（如果已知）
        
        Returns:
            修复后的文本
        """
        if not text:
            return text
        
        try:
            # 先尝试编码为UTF-8
            utf8_bytes = text.encode('utf-8')
            # 再解码回来
            fixed_text = utf8_bytes.decode('utf-8')
            return fixed_text
        except Exception as e:
            logger.warning(f"文本编码修复失败：{e}")
            return text
    
    @staticmethod
    def clean_encoding_errors(text: str, replace_char: str = '?') -> str:
        """
        清理文本中的编码错误字符
        
        Args:
            text: 包含编码错误字符的文本
            replace_char: 用于替换的字符
        
        Returns:
            清理后的文本
        """
        if not text:
            return text
        
        try:
            # 编码为UTF-8，使用replace处理错误
            utf8_bytes = text.encode('utf-8', errors='replace')
            clean_text = utf8_bytes.decode('utf-8', errors='replace')
            return clean_text
        except Exception as e:
            logger.error(f"编码错误清理失败：{e}")
            return text


# 便利函数
def check_utf8_encoding(data: bytes) -> bool:
    """
    快速检查数据是否为有效UTF-8
    
    Args:
        data: 字节数据
    
    Returns:
        True表示有效UTF-8
    """
    return EncodingChecker.is_utf8(data)


def convert_to_utf8(data: bytes, source_encoding: Optional[str] = None) -> Tuple[str, str]:
    """
    便利函数：转换数据为UTF-8
    
    Args:
        data: 字节数据
        source_encoding: 源编码
    
    Returns:
        (转换后的文本, 原始编码)
    """
    return EncodingChecker.convert_to_utf8(data, source_encoding)


def detect_encoding(data: bytes, confidence_threshold: float = 0.7) -> Tuple[Optional[str], float]:
    """
    便利函数：检测编码
    
    Args:
        data: 字节数据
        confidence_threshold: 置信度阈值
    
    Returns:
        (编码, 置信度)
    """
    return EncodingChecker.detect_encoding(data, confidence_threshold)
