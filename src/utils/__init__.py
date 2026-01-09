# -*- coding: utf-8 -*-
"""
工具函数模块

提供数据清洗项目所需的各类工具函数，包括：
- 日志管理
- 编码检查和修复
- 异常处理
- 数据验证
- 时间处理
- 字符串处理
- 统计功能
"""

from src.utils.logger import get_logger, setup_logger
from src.utils.encoding_checker import EncodingChecker, check_utf8_encoding, convert_to_utf8
from src.utils.error_handler import ErrorHandler, handle_error, log_error
from src.utils.validation import Validator, validate_range, validate_pattern
from src.utils.time_utils import TimeUtils, standardize_timestamp, convert_relative_to_absolute
from src.utils.string_utils import StringUtils, remove_whitespace, remove_special_chars
from src.utils.statistics import Statistics, calculate_dedup_rate, calculate_missing_rate

__all__ = [
    "get_logger",
    "setup_logger",
    "EncodingChecker",
    "check_utf8_encoding",
    "convert_to_utf8",
    "ErrorHandler",
    "handle_error",
    "log_error",
    "Validator",
    "validate_range",
    "validate_pattern",
    "TimeUtils",
    "standardize_timestamp",
    "convert_relative_to_absolute",
    "StringUtils",
    "remove_whitespace",
    "remove_special_chars",
    "Statistics",
    "calculate_dedup_rate",
    "calculate_missing_rate",
]
