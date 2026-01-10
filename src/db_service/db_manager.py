# -*- coding: utf-8 -*-
"""
数据库管理模块

负责数据库连接、数据操作、事务管理等。

支持的数据库：MySQL、PostgreSQL、SQLite

设计理念：
- 单例模式管理数据库连接
- 支持连接池
- 自动处理SQL注入预防
- 事务支持
"""

from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import traceback

from config.db_credentials import DatabaseCredentials
from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler

logger = get_logger(__name__)


class DatabaseManager:
    """
    数据库管理器
    
    负责：
    1. 数据库连接管理（连接池）
    2. SQL执行和事务管理
    3. 数据插入、查询、更新、删除
    4. 表结构管理
    """
    
    # 单例实例
    _instance = None
    _engine = None
    _session_maker = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化数据库管理器"""
        if self._initialized:
            return
        
        self._initialized = True
        self._init_engine()
    
    @classmethod
    def _init_engine(cls) -> None:
        """初始化数据库引擎"""
        try:
            credentials = DatabaseCredentials()
            connection_string = credentials.get_connection_string()
            
            logger.info(f"正在初始化数据库连接：{connection_string.split('/')[-1]}")
            
            # 根据数据库类型选择连接池
            db_type = credentials.get_type()
            
            if db_type == 'sqlite':
                # SQLite不需要连接池
                cls._engine = create_engine(connection_string, poolclass=NullPool)
            else:
                # MySQL/PostgreSQL使用连接池
                cls._engine = create_engine(
                    connection_string,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False
                )
            
            # 创建会话工厂
            cls._session_maker = sessionmaker(bind=cls._engine)
            
            # 测试连接
            with cls._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("数据库连接成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败：{e}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"数据库连接失败：{e}")
    
    @contextmanager
    def get_session(self):
        """
        获取数据库会话
        
        Yields:
            SQLAlchemy Session对象
        
        示例：
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT * FROM table"))
        """
        session = self._session_maker()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"会话执行出错，已回滚：{e}")
            raise
        finally:
            session.close()
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        执行SQL查询（SELECT）
        
        Args:
            sql: SQL查询语句
            params: 参数字典（用于防止SQL注入）
        
        Returns:
            查询结果（列表，每项为字典）
        
        示例：
            result = db_manager.execute_sql(
                "SELECT * FROM products WHERE id = :id",
                {"id": 123}
            )
        """
        try:
            with self.get_session() as session:
                if params:
                    result = session.execute(text(sql), params)
                else:
                    result = session.execute(text(sql))
                
                # 转换为字典列表
                rows = [dict(row) for row in result]
                logger.debug(f"SQL查询完成，返回{len(rows)}条记录")
                return rows
                
        except Exception as e:
            logger.error(f"SQL执行失败：{sql}，错误：{e}")
            raise RuntimeError(f"SQL执行失败：{e}")
    
    def insert_records(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> Tuple[int, int]:
        """
        批量插入记录
        
        Args:
            table_name: 表名
            records: 要插入的记录列表
            batch_size: 批次大小（每batch_size条记录提交一次）
        
        Returns:
            (成功插入记录数, 失败记录数)
        
        示例：
            success, failed = db_manager.insert_records(
                "products",
                [{"id": 1, "name": "商品1"}, {"id": 2, "name": "商品2"}]
            )
        """
        if not records:
            logger.warning("没有要插入的记录")
            return 0, 0
        
        success_count = 0
        failed_count = 0
        
        try:
            with self.get_session() as session:
                # 分批处理
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    try:
                        # 构建INSERT语句
                        if batch:
                            # 执行批量插入
                            for record in batch:
                                try:
                                    # 过滤掉NULL值的字段（让数据库使用默认值）
                                    non_null_record = {k: v for k, v in record.items() if v is not None}
                                    
                                    if not non_null_record:
                                        # 如果所有字段都是NULL，跳过
                                        logger.warning(f"记录所有字段都为NULL，跳过：{record}")
                                        failed_count += 1
                                        continue
                                    
                                    columns = list(non_null_record.keys())
                                    placeholders = ', '.join([f':{col}' for col in columns])
                                    column_names = ', '.join(columns)
                                    
                                    sql = f"""
                                        INSERT INTO {table_name} ({column_names})
                                        VALUES ({placeholders})
                                    """
                                    
                                    session.execute(text(sql), non_null_record)
                                    success_count += 1
                                except Exception as e:
                                    logger.warning(f"单条记录插入失败：{record}，错误：{e}")
                                    failed_count += 1
                        
                        # 提交批次
                        session.commit()
                        logger.info(f"批次{i//batch_size + 1}提交：成功{success_count}条，失败{failed_count}条")
                        
                    except Exception as e:
                        session.rollback()
                        logger.error(f"批次{i//batch_size + 1}失败，已回滚：{e}")
                        failed_count += len(batch)
            
            logger.info(f"记录插入完成：成功{success_count}条，失败{failed_count}条")
            return success_count, failed_count
            
        except Exception as e:
            logger.error(f"批量插入失败：{e}")
            return 0, len(records)
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
        
        Returns:
            True表示存在，False表示不存在
        """
        try:
            inspector = inspect(self._engine)
            tables = inspector.get_table_names()
            return table_name in tables
        except Exception as e:
            logger.error(f"检查表是否存在失败：{e}")
            return False
    
    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """
        获取表的列信息
        
        Args:
            table_name: 表名
        
        Returns:
            列名到列类型的映射
        """
        try:
            inspector = inspect(self._engine)
            columns = inspector.get_columns(table_name)
            return {col['name']: str(col['type']) for col in columns}
        except Exception as e:
            logger.error(f"获取表列信息失败：{e}")
            return {}
    
    def execute_update(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        执行UPDATE语句
        
        Args:
            sql: UPDATE SQL语句
            params: 参数字典
        
        Returns:
            受影响的行数
        """
        try:
            with self.get_session() as session:
                if params:
                    result = session.execute(text(sql), params)
                else:
                    result = session.execute(text(sql))
                
                session.commit()
                affected_rows = result.rowcount
                logger.info(f"UPDATE完成：受影响行数{affected_rows}")
                return affected_rows
                
        except Exception as e:
            logger.error(f"UPDATE执行失败：{sql}，错误：{e}")
            raise RuntimeError(f"UPDATE执行失败：{e}")
    
    def close(self) -> None:
        """关闭数据库连接池"""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接池失败：{e}")


# 全局实例
_db_manager = None


def get_database_manager() -> DatabaseManager:
    """
    获取数据库管理器单例
    
    Returns:
        DatabaseManager实例
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def insert_records(
    table_name: str,
    records: List[Dict[str, Any]],
    batch_size: int = 1000
) -> Tuple[int, int]:
    """
    便利函数：批量插入记录
    
    Args:
        table_name: 表名
        records: 记录列表
        batch_size: 批次大小
    
    Returns:
        (成功数, 失败数)
    """
    db_manager = get_database_manager()
    return db_manager.insert_records(table_name, records, batch_size)


def query_records(
    sql: str,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    """
    便利函数：查询记录
    
    Args:
        sql: SQL查询语句
        params: 参数字典
    
    Returns:
        查询结果（字典列表）
    """
    db_manager = get_database_manager()
    return db_manager.execute_sql(sql, params)
