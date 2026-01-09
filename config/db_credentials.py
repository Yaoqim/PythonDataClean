# -*- coding: utf-8 -*-
"""
数据库凭证管理模块

本模块负责管理数据库连接凭证，支持从环境变量或配置文件加载。
遵循安全最佳实践：敏感信息不应该硬编码在代码中。
"""

import os
from typing import Dict, Any, Optional


class DatabaseCredentials:
    """
    数据库凭证管理器
    
    负责：
    1. 从环境变量加载数据库连接信息
    2. 支持多数据库类型（MySQL、PostgreSQL、SQLite）
    3. 提供安全的凭证访问接口
    """
    
    def __init__(self):
        """初始化数据库凭证"""
        self._credentials = {}
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """
        从环境变量加载数据库凭证
        
        支持以下环境变量：
        - DB_TYPE: 数据库类型 (postgresql/mysql/sqlite)
        - DB_HOST: 数据库服务器地址
        - DB_PORT: 数据库服务器端口
        - DB_NAME: 数据库名称
        - DB_USER: 数据库用户名
        - DB_PASSWORD: 数据库密码
        - DB_CHARSET: 字符集（默认utf8mb4）
        """
        # 主数据库配置
        self._credentials['primary'] = {
            'type': os.getenv('DB_TYPE', 'mysql'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', 'data_clean'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4'),
        }
        
        # 支持SQLite用于本地开发
        if self._credentials['primary']['type'] == 'sqlite':
            self._credentials['primary']['database'] = os.getenv(
                'DB_PATH', 
                'data_clean.db'
            )
    
    def get_credentials(self, database_name: str = 'primary') -> Dict[str, Any]:
        """
        获取指定数据库的凭证
        
        Args:
            database_name: 数据库名称，默认为'primary'
        
        Returns:
            包含连接信息的字典
        
        Raises:
            KeyError: 如果指定的数据库配置不存在
        """
        if database_name not in self._credentials:
            raise KeyError(f"数据库配置'{database_name}'不存在")
        
        return self._credentials[database_name].copy()
    
    def get_connection_string(self, database_name: str = 'primary') -> str:
        """
        根据凭证生成SQLAlchemy连接字符串
        
        Args:
            database_name: 数据库名称
        
        Returns:
            SQLAlchemy连接字符串
        
        示例：
            postgresql://user:password@localhost:5432/database_name
            mysql+pymysql://user:password@localhost:3306/database_name
            sqlite:///data_clean.db
        """
        creds = self.get_credentials(database_name)
        db_type = creds['type'].lower()
        
        if db_type == 'sqlite':
            # SQLite连接字符串
            return f"sqlite:///{creds['database']}"
        
        elif db_type == 'postgresql':
            # PostgreSQL连接字符串
            user = creds['user']
            password = creds['password']
            host = creds['host']
            port = creds['port']
            database = creds['database']
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        elif db_type == 'mysql':
            # MySQL连接字符串（使用pymysql驱动）
            user = creds['user']
            password = creds['password']
            host = creds['host']
            port = creds['port']
            database = creds['database']
            charset = creds.get('charset', 'utf8mb4')
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
        
        else:
            raise ValueError(f"不支持的数据库类型：{db_type}")
    
    def validate(self) -> bool:
        """
        验证凭证配置是否完整
        
        Returns:
            True表示配置有效，False表示配置不完整
        """
        creds = self._credentials.get('primary', {})
        
        # 检查必填字段
        required_fields = ['type', 'host', 'port', 'database', 'user', 'password']
        for field in required_fields:
            if not creds.get(field):
                return False
        
        # 如果是SQLite，只需要database（文件路径）
        if creds['type'] == 'sqlite':
            return bool(creds.get('database'))
        
        return True


# 全局凭证实例
_credentials_instance: Optional[DatabaseCredentials] = None


def get_credentials() -> DatabaseCredentials:
    """
    获取全局数据库凭证实例（单例模式）
    
    Returns:
        DatabaseCredentials实例
    """
    global _credentials_instance
    if _credentials_instance is None:
        _credentials_instance = DatabaseCredentials()
    return _credentials_instance
