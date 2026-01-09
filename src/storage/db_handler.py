from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database_config import DatabaseConfig
import pandas as pd

class DatabaseHandler:
    """
    【已弃用】数据库处理器
    
    ⚠️ 此类已废弃，不应再使用
    
    迁移说明：
    - 新代码应使用 src.db_service.db_manager.DatabaseManager
    - 此类仅保留用于向后兼容
    - 计划在下一个主版本中删除
    
    废弃原因：
    - DatabaseManager 提供更完善的连接池管理
    - 支持事务管理和错误处理
    - 适配多数据库类型
    """
    
    def __init__(self):
        self.engine = create_engine(DatabaseConfig.get_connection_string())
        self.Session = sessionmaker(bind=self.engine)
    
    def save_data(self, data: pd.DataFrame, table_name: str):
        """保存数据到数据库"""
        try:
            data.to_sql(table_name, self.engine, if_exists='append', index=False)
            print(f"数据已保存到表: {table_name}")
        except Exception as e:
            print(f"保存失败: {e}")
            raise
    
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
