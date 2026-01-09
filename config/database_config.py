class DatabaseConfig:
    """
    【已弃用】数据库连接配置
    
    ⚠️ 此类已废弃，不应再使用
    
    迁移说明：
    - 新代码应使用 config.db_credentials.DatabaseCredentials
    - 此类仅保留用于向后兼容
    - 计划在下一个主版本中删除
    """
    DB_TYPE = "mysql"
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_NAME = "data_clean"
    
    @classmethod
    def get_connection_string(cls):
        """获取数据库连接字符串"""
        if cls.DB_TYPE == "sqlite":
            return f"sqlite:///./data_clean.db"
        elif cls.DB_TYPE == "mysql":
            return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset=utf8mb4"
        elif cls.DB_TYPE == "postgresql":
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        else:
            raise ValueError(f"不支持的数据库类型：{cls.DB_TYPE}")
