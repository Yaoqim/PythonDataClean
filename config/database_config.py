class DatabaseConfig:
    """数据库连接配置"""
    DB_TYPE = "sqlite"
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_NAME = "data_cleaning"
    
    @classmethod
    def get_connection_string(cls):
        """获取数据库连接字符串"""
        if cls.DB_TYPE == "sqlite":
            return f"sqlite:///./data_cleaning.db"
        elif cls.DB_TYPE == "mysql":
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        elif cls.DB_TYPE == "postgresql":
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
