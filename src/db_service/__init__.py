# -*- coding: utf-8 -*-
"""
数据库服务模块

负责与数据库交互，包括连接管理、数据插入、查询等操作。

模块功能：
1. db_manager.py - 数据库连接和操作管理
"""

from src.db_service.db_manager import DatabaseManager, insert_records, query_records

__all__ = [
    "DatabaseManager",
    "insert_records",
    "query_records",
]
