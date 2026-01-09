# -*- coding: utf-8 -*-
"""
日志管理模块

提供统一的日志管理系统，支持：
- 多级别日志（DEBUG、INFO、WARNING、ERROR）
- 日志轮转（按大小和日期）
- 自动清理过期日志
"""

import os
import logging
import logging.handlers
from typing import Optional
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import (
    LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    LOG_FILE_MAX_SIZE_MB, LOG_FILE_BACKUP_COUNT, LOG_RETENTION_DAYS
)


class LoggerManager:
    """
    日志管理器
    
    负责：
    1. 创建和配置日志器
    2. 设置日志处理器（文件、控制台）
    3. 管理日志文件轮转
    4. 自动清理过期日志
    """
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup_logger(cls, name: str) -> logging.Logger:
        """
        获取或创建日志器
        
        Args:
            name: 日志器名称（通常为模块名）
        
        Returns:
            配置好的Logger实例
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        # 创建日志目录
        log_dir = Path(LOG_DIR)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志器
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # 清除已有的处理器
        logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器（轮转）
        log_file = log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=LOG_FILE_MAX_SIZE_MB * 1024 * 1024,
            backupCount=LOG_FILE_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 防止日志重复
        logger.propagate = False
        
        cls._loggers[name] = logger
        
        # 首次初始化时清理过期日志
        if not cls._initialized:
            cls._clean_old_logs()
            cls._initialized = True
        
        return logger
    
    @classmethod
    def _clean_old_logs(cls) -> None:
        """
        清理过期日志文件
        
        按照 LOG_RETENTION_DAYS 配置删除超期的日志文件
        """
        log_dir = Path(LOG_DIR)
        if not log_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
        
        try:
            for log_file in log_dir.glob("*.log*"):
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # 删除过期文件
                if file_mtime < cutoff_date:
                    log_file.unlink()
                    print(f"已删除过期日志文件：{log_file}")
        except Exception as e:
            print(f"清理过期日志时出错：{e}")


# 全局日志器实例
_loggers_cache = {}


def setup_logger(name: str) -> logging.Logger:
    """
    设置并返回日志器
    
    Args:
        name: 日志器名称（通常为 __name__）
    
    Returns:
        配置好的Logger实例
    
    示例：
        logger = setup_logger(__name__)
        logger.info("这是一条信息日志")
    """
    return LoggerManager.setup_logger(name)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器（单例）
    
    Args:
        name: 日志器名称
    
    Returns:
        Logger实例
    """
    if name not in _loggers_cache:
        _loggers_cache[name] = setup_logger(name)
    return _loggers_cache[name]
