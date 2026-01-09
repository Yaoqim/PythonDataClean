# -*- coding: utf-8 -*-
"""
存储模块

负责将清洗后的数据存入数据库。
"""

from src.storage.storage_strategy import StorageStrategy, store_records

__all__ = ["StorageStrategy", "store_records"]
