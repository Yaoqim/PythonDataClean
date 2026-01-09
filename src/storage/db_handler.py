from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database_config import DatabaseConfig
import pandas as pd

class DatabaseHandler:
    """数据库处理器"""
    
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
