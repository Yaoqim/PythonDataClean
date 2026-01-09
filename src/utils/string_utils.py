# -*- coding: utf-8 -*-
"""
字符串处理模块

提供文本清洁、规范化等功能：
- 去空格、去特殊字符
- 去emoji和表情符号
- 大小写规范化
- HTML标签移除
- 文本截断
"""

import re
from typing import Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StringUtils:
    """
    字符串处理工具类
    
    提供各种文本处理功能
    """
    
    # Emoji和特殊表情正则 - 简化版本
    EMOJI_PATTERN = re.compile(
        r"[\U0001F300-\U0001F9FF]|[\u2600-\u27BF]|[\u2300-\u23FF]|[\u2000-\u206F]",
        flags=re.UNICODE
    )
    
    # HTML标签正则
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    
    # URL正则
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    # @提及正则
    AT_MENTION_PATTERN = re.compile(r'@[a-zA-Z0-9_\u4e00-\u9fff]+')
    
    @staticmethod
    def remove_whitespace(text: str, preserve_internal: bool = True) -> str:
        """
        移除文本中的空格
        
        Args:
            text: 输入文本
            preserve_internal: 是否保留内部空格（仅移除首尾）
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        if preserve_internal:
            # 只移除首尾空格和制表符
            return text.strip()
        else:
            # 移除所有空格
            return re.sub(r'\s+', '', text)
    
    @staticmethod
    def remove_special_chars(
        text: str,
        keep_punctuation: bool = False
    ) -> str:
        """
        移除文本中的特殊字符
        
        Args:
            text: 输入文本
            keep_punctuation: 是否保留标点符号
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        if keep_punctuation:
            # 只移除特殊字符，保留字母、数字、标点
            return re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\s.,!?;:\'"()（），。！？；：\'"]', '', text)
        else:
            # 移除所有特殊字符，只保留字母、数字、中文
            return re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\s]', '', text)
    
    @staticmethod
    def remove_emoji(text: str, replace_char: str = '') -> str:
        """
        移除文本中的emoji和特殊表情符号
        
        Args:
            text: 输入文本
            replace_char: 替换字符（默认为空）
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        # 移除emoji
        text = StringUtils.EMOJI_PATTERN.sub(replace_char, text)
        return text
    
    @staticmethod
    def remove_html_tags(text: str, replace_char: str = '') -> str:
        """
        移除HTML标签
        
        Args:
            text: 输入文本
            replace_char: 替换字符
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        # 移除HTML标签
        text = StringUtils.HTML_TAG_PATTERN.sub(replace_char, text)
        
        # 处理HTML实体
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        
        return text
    
    @staticmethod
    def remove_urls(text: str, replace_char: str = '') -> str:
        """
        移除URL链接
        
        Args:
            text: 输入文本
            replace_char: 替换字符
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        return StringUtils.URL_PATTERN.sub(replace_char, text)
    
    @staticmethod
    def remove_at_mentions(text: str, replace_char: str = '') -> str:
        """
        移除@提及
        
        Args:
            text: 输入文本
            replace_char: 替换字符
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        return StringUtils.AT_MENTION_PATTERN.sub(replace_char, text)
    
    @staticmethod
    def normalize_case(text: str, case: str = "lower") -> str:
        """
        规范化文本大小写
        
        Args:
            text: 输入文本
            case: 目标大小写（lower/upper/title）
        
        Returns:
            处理后的文本
        """
        if not text:
            return text
        
        if case == "lower":
            return text.lower()
        elif case == "upper":
            return text.upper()
        elif case == "title":
            return text.title()
        else:
            return text
    
    @staticmethod
    def truncate_text(
        text: str,
        max_length: int,
        suffix: str = "..."
    ) -> str:
        """
        截断文本到指定长度
        
        Args:
            text: 输入文本
            max_length: 最大长度
            suffix: 后缀（附加到截断文本后）
        
        Returns:
            截断后的文本
        """
        if not text or len(text) <= max_length:
            return text
        
        truncated = text[:max_length - len(suffix)]
        return truncated + suffix
    
    @staticmethod
    def clean_text(
        text: str,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_emoji: bool = True,
        remove_mentions: bool = True,
        max_length: Optional[int] = None
    ) -> str:
        """
        综合清洁文本
        
        一次性应用多个清洁规则
        
        Args:
            text: 输入文本
            remove_html: 是否移除HTML标签
            remove_urls: 是否移除URL
            remove_emoji: 是否移除emoji
            remove_mentions: 是否移除@提及
            max_length: 最大长度（如果指定会截断）
        
        Returns:
            清洁后的文本
        """
        if not text:
            return text
        
        # 应用各个清洁规则
        if remove_html:
            text = StringUtils.remove_html_tags(text)
        
        if remove_urls:
            text = StringUtils.remove_urls(text)
        
        if remove_emoji:
            text = StringUtils.remove_emoji(text)
        
        if remove_mentions:
            text = StringUtils.remove_at_mentions(text)
        
        # 多余空格规范化
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 截断到指定长度
        if max_length and len(text) > max_length:
            text = StringUtils.truncate_text(text, max_length)
        
        return text


# 便利函数
def remove_whitespace(text: str, preserve_internal: bool = True) -> str:
    """快速移除空格"""
    return StringUtils.remove_whitespace(text, preserve_internal)


def remove_special_chars(text: str, keep_punctuation: bool = False) -> str:
    """快速移除特殊字符"""
    return StringUtils.remove_special_chars(text, keep_punctuation)


def clean_text(
    text: str,
    remove_html: bool = True,
    remove_urls: bool = True,
    remove_emoji: bool = True,
    remove_mentions: bool = True,
    max_length: Optional[int] = None
) -> str:
    """快速综合清洁文本"""
    return StringUtils.clean_text(
        text, remove_html, remove_urls, remove_emoji, remove_mentions, max_length
    )
