# -*- coding: utf-8 -*-
"""
数据库凭证管理模块

本模块负责管理数据库连接凭证，统一从YAML配置文件读取。
遵循安全最佳实践：敏感信息不应该硬编码在代码中。
"""

from typing import Dict, Any, Optional
from config import yaml_loader


class DatabaseCredentials:
    """
    数据库凭证管理器
    
    负责：
    1. 从YAML配置文件加载数据库连接信息
    2. 支持多数据库类型（MySQL、PostgreSQL、SQLite）
    3. 提供安全的凭证访问接口
    """
    
    def __init__(self):
        """初始化数据库凭证"""
        self._credentials = {}
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """
        从YAML配置文件加载数据库凭证
        """
        db_config = yaml_loader.get_db_config()
        
        # 主数据库配置
        self._credentials['primary'] = {
            'type': db_config.get('type', 'mysql'),
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 3306),
            'database': db_config.get('name', 'data_clean'),
            'user': db_config.get('user', 'root'),
            'password': db_config.get('password', ''),
            'charset': db_config.get('charset', 'utf8mb4'),
        }
        
        # 支持SQLite用于本地开发
        if self._credentials['primary']['type'] == 'sqlite':
            self._credentials['primary']['database'] = db_config.get('name') or 'data_clean.db'
    
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
    
    def get_type(self, database_name: str = 'primary') -> str:
        """
        获取数据库类型
        
        Args:
            database_name: 数据库名称，默认为'primary'
        
        Returns:
            数据库类型（sqlite、mysql、postgresql）
        """
        creds = self.get_credentials(database_name)
        return creds['type']
    
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
