# -*- coding: utf-8 -*-
"""检查数据库表结构"""

from config.db_credentials import DatabaseCredentials
from sqlalchemy import create_engine, inspect

credentials = DatabaseCredentials()
connection_string = credentials.get_connection_string()
engine = create_engine(connection_string)

inspector = inspect(engine)
columns = inspector.get_columns('ec_product_info')

print('\nec_product_info 表的列：')
for col in columns:
    print(f"  • {col['name']:20s} {str(col['type']):30s}")
