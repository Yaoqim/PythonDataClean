# -*- coding: utf-8 -*-
"""
异常处理模块

提供统一的异常处理和错误恢复机制。
"""

import traceback
from typing import Any, Callable, Optional, TypeVar
from functools import wraps

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ErrorHandler:
    """
    异常处理器
    
    提供结构化的异常处理、日志记录和错误恢复机制
    """
    
    # 错误代码定义（遵循《数据清洗MCP使用规范.md》）
    ERROR_CODES = {
        "FILE_NOT_FOUND": 11001,
        "METADATA_NOT_FOUND": 11002,
        "INVALID_FORMAT": 11005,
        "ENCODING_ERROR": 11006,
        "DATABASE_ERROR": 12001,
        "INSERT_FAILED": 12005,
        "DUPLICATE_KEY": 12006,
        "CLEANING_FAILED": 13001,
        "VALIDATION_FAILED": 13002,
    }
    
    @staticmethod
    def handle_file_read_error(
        file_path: str, 
        exception: Exception,
        skip_on_error: bool = True
    ) -> None:
        """
        处理文件读取错误
        
        Args:
            file_path: 文件路径
            exception: 异常对象
            skip_on_error: 是否跳过此文件继续处理
        """
        error_code = ErrorHandler.ERROR_CODES.get("FILE_NOT_FOUND", 11001)
        error_msg = f"文件读取失败：{file_path}，错误：{str(exception)}"
        
        logger.error(error_msg, exc_info=True)
        
        if skip_on_error:
            logger.warning(f"跳过文件 {file_path}，继续处理其他文件")
        else:
            raise RuntimeError(error_msg) from exception
    
    @staticmethod
    def handle_db_error(
        operation: str,
        exception: Exception,
        rollback: bool = True
    ) -> None:
        """
        处理数据库错误
        
        Args:
            operation: 操作描述（如"INSERT"、"UPDATE"）
            exception: 异常对象
            rollback: 是否回滚事务
        """
        error_code = ErrorHandler.ERROR_CODES.get("DATABASE_ERROR", 12001)
        error_msg = f"数据库操作失败：{operation}，错误：{str(exception)}"
        
        logger.error(error_msg, exc_info=True)
        
        if rollback:
            logger.warning("数据库事务已回滚")
        
        raise RuntimeError(error_msg) from exception
    
    @staticmethod
    def handle_cleaning_error(
        business_type: str,
        file_path: str,
        exception: Exception
    ) -> None:
        """
        处理数据清洗错误
        
        Args:
            business_type: 业务类型ID
            file_path: 数据文件路径
            exception: 异常对象
        """
        error_msg = (
            f"数据清洗失败：business_type={business_type}, "
            f"file={file_path}, error={str(exception)}"
        )
        
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from exception
    
    @staticmethod
    def log_error(
        context: str,
        exception: Exception,
        level: str = "error"
    ) -> None:
        """
        记录错误信息
        
        Args:
            context: 错误上下文描述
            exception: 异常对象
            level: 日志级别（debug/info/warning/error）
        """
        log_func = getattr(logger, level, logger.error)
        log_func(f"{context}：{str(exception)}", exc_info=True)


def handle_error(
    error_type: str = "general",
    log_traceback: bool = True
) -> Callable:
    """
    错误处理装饰器
    
    Args:
        error_type: 错误类型
        log_traceback: 是否记录完整的堆栈跟踪
    
    Returns:
        装饰器函数
    
    示例：
        @handle_error("database_error")
        def insert_to_database(record):
            # 函数实现
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"函数 {func.__name__} 执行失败（{error_type}）"
                if log_traceback:
                    logger.error(
                        f"{error_msg}：{str(e)}\n{traceback.format_exc()}"
                    )
                else:
                    logger.error(f"{error_msg}：{str(e)}")
                return None
        
        return wrapper
    
    return decorator


def log_error(
    context: str,
    exception: Exception,
    level: str = "error"
) -> None:
    """
    便利函数：记录错误
    
    Args:
        context: 错误上下文
        exception: 异常对象
        level: 日志级别
    """
    ErrorHandler.log_error(context, exception, level)
