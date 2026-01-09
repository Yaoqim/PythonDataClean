# -*- coding: utf-8 -*-
"""
数据库管理模块

核心职责：
1. 数据库连接管理
2. 记录插入（单条、批量）
3. 存储信息查询
"""

from typing import Dict, Any, Optional, List
import datetime

from sqlalchemy import create_engine, Table, MetaData, insert
from sqlalchemy.orm import sessionmaker, Session

from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler
from config.db_credentials import DatabaseCredentials
from src.metadata.business_type_registry import BusinessTypeRegistry

logger = get_logger(__name__)


class DatabaseManager:
    """
    数据库管理器
    
    负责：
    1. 数据库连接
    2. 记录插入和查询
    3. 存储位置追踪
    """
    
    _instance = None
    _engine = None
    _session_maker = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化数据库连接"""
        if self._engine is None:
            self._init_engine()
    
    @classmethod
    def _init_engine(cls):
        """初始化数据库引擎"""
        try:
            credentials = DatabaseCredentials()
            connection_string = credentials.get_connection_string()
            
            cls._engine = create_engine(connection_string, pool_size=10, max_overflow=20)
            cls._session_maker = sessionmaker(bind=cls._engine)
            
            # 测试连接
            with cls._engine.connect() as conn:
                conn.execute("SELECT 1")
            
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败：{e}")
            ErrorHandler.handle_db_error(e)
    
    def insert_records(
        self,
        business_type_id: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        插入清洗后的记录
        
        Args:
            business_type_id: 业务类型ID
            records: 记录列表
        
        Returns:
            存储信息字典
        """
        if not records:
            logger.warning("无记录可插入")
            return {
                'success': False,
                'inserted_count': 0,
                'table_name': None,
                'error': '无记录'
            }
        
        try:
            table_name = BusinessTypeRegistry.get_table_name(business_type_id)
            if not table_name:
                raise ValueError(f"未找到业务类型的表名：{business_type_id}")
            
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self._engine)
            
            session = self._session_maker()
            
            try:
                # 批量插入
                stmt = insert(table).values(records)
                result = session.execute(stmt)
                session.commit()
                
                inserted_count = result.rowcount if result.rowcount else len(records)
                
                logger.info(f"成功插入{inserted_count}条记录到表{table_name}")
                
                return {
                    'success': True,
                    'inserted_count': inserted_count,
                    'table_name': table_name,
                    'business_type_id': business_type_id,
                    'insert_time': datetime.datetime.now().isoformat(),
                    'database': self._get_db_name(),
                    'key_fields': self._get_key_fields(business_type_id),
                    'time_range': self._get_time_range(records)
                }
            finally:
                session.close()
        
        except Exception as e:
            logger.error(f"插入记录失败：{e}")
            ErrorHandler.handle_db_error(e)
            return {
                'success': False,
                'inserted_count': 0,
                'table_name': table_name,
                'error': str(e)
            }
    
    def _get_db_name(self) -> str:
        """获取数据库名称"""
        credentials = DatabaseCredentials()
        return credentials.get_credentials().get('database', 'default')
    
    def _get_key_fields(self, business_type_id: str) -> List[str]:
        """获取关键字段"""
        fields = BusinessTypeRegistry.get_fields(business_type_id)
        return list(fields.keys()) if fields else []
    
    def _get_time_range(self, records: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """从记录中提取时间范围"""
        if not records:
            return None
        
        # 查找可能的时间字段
        time_fields = ['create_time', 'crawl_date', 'update_time', 'timestamp']
        
        for record in records:
            for field in time_fields:
                if field in record:
                    return {
                        'field': field,
                        'min': str(record[field]),
                        'max': str(record[field])
                    }
        
        return None
    
    def query_records(self, business_type_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询最近插入的记录
        
        Args:
            business_type_id: 业务类型ID
            limit: 限制数量
        
        Returns:
            记录列表
        """
        try:
            table_name = BusinessTypeRegistry.get_table_name(business_type_id)
            
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self._engine)
            
            session = self._session_maker()
            
            try:
                result = session.query(table).limit(limit).all()
                return [dict(row) for row in result]
            finally:
                session.close()
        
        except Exception as e:
            logger.error(f"查询记录失败：{e}")
            return []


# 便利函数
def get_db_manager() -> DatabaseManager:
    """获取数据库管理器单例"""
    return DatabaseManager()
