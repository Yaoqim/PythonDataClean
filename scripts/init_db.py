# -*- coding: utf-8 -*-
"""
数据库初始化脚本

创建所有业务类型所需的数据库表
执行方式: python scripts/init_db.py
"""

import sys
import os
from pathlib import Path

# 添加项目根路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from config.db_credentials import DatabaseCredentials
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, DateTime, Text, JSON

logger = get_logger(__name__)


# 表定义
TABLES_SCHEMA = {
    'ec_goods_phone': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('product_id', String(100), unique=True, nullable=False, index=True),
        Column('product_name', String(255)),
        Column('category', String(100)),
        Column('price', Float),
        Column('sales', Integer),
        Column('rating', Float),
        Column('description', Text),
        Column('created_at', DateTime, default=sa.func.now()),
        Column('updated_at', DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    ],
    'ec_comment': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('comment_id', String(100), unique=True, nullable=False, index=True),
        Column('product_id', String(100)),
        Column('user_id', String(100), index=True),
        Column('content', Text),
        Column('rating', Integer),
        Column('create_time', DateTime),
        Column('helpful_count', Integer),
        Column('sentiment', String(50)),
        Column('sentiment_confidence', Float),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'customer_dialog': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('dialog_id', String(100), unique=True, nullable=False, index=True),
        Column('customer_id', String(100), index=True),
        Column('agent_id', String(100), index=True),
        Column('messages', JSON),
        Column('sentiment', String(50)),
        Column('sentiment_confidence', Float),
        Column('topic', String(100)),
        Column('topic_confidence', Float),
        Column('duration', Integer),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'social_comment': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('comment_id', String(100), unique=True, nullable=False, index=True),
        Column('author_id', String(100), index=True),
        Column('content', Text),
        Column('platform', String(50)),
        Column('likes', Integer),
        Column('create_time', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'social_post': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('post_id', String(100), unique=True, nullable=False, index=True),
        Column('author_id', String(100), index=True),
        Column('content', Text),
        Column('likes', Integer),
        Column('shares', Integer),
        Column('comments_count', Integer),
        Column('create_time', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'news_article': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('article_id', String(100), unique=True, nullable=False, index=True),
        Column('title', String(255)),
        Column('content', Text),
        Column('source', String(255)),
        Column('category', String(100)),
        Column('views', Integer),
        Column('publish_time', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'finance_report': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('report_id', String(100), unique=True, nullable=False, index=True),
        Column('company_id', String(100), index=True),
        Column('revenue', Float),
        Column('profit', Float),
        Column('report_type', String(50)),
        Column('report_date', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'enterprise_info': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('company_id', String(100), unique=True, nullable=False, index=True),
        Column('company_name', String(255)),
        Column('registration_number', String(100), unique=True),
        Column('founded_date', DateTime),
        Column('industry', String(100)),
        Column('employee_count', Integer),
        Column('status', String(50)),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'recruit_job': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('job_id', String(100), unique=True, nullable=False, index=True),
        Column('job_title', String(255)),
        Column('company_id', String(100), index=True),
        Column('salary_min', Float),
        Column('salary_max', Float),
        Column('location', String(100)),
        Column('job_type', String(50)),
        Column('publish_date', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'video_metadata': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('video_id', String(100), unique=True, nullable=False, index=True),
        Column('title', String(255)),
        Column('description', Text),
        Column('author_id', String(100), index=True),
        Column('duration', Integer),
        Column('views', Integer),
        Column('likes', Integer),
        Column('tags', JSON),
        Column('upload_time', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'user_profile': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('user_id', String(100), unique=True, nullable=False, index=True),
        Column('username', String(255)),
        Column('email', String(255), unique=True),
        Column('phone', String(20)),
        Column('age', Integer),
        Column('gender', String(10)),
        Column('city', String(100)),
        Column('registration_date', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'property_info': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('property_id', String(100), unique=True, nullable=False, index=True),
        Column('property_name', String(255)),
        Column('location', String(255)),
        Column('price', Float),
        Column('area', Float),
        Column('rooms', Integer),
        Column('property_type', String(50)),
        Column('list_date', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'car_info': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('car_id', String(100), unique=True, nullable=False, index=True),
        Column('brand', String(100)),
        Column('model', String(255)),
        Column('price', Float),
        Column('year', Integer),
        Column('mileage', Float),
        Column('fuel_type', String(50)),
        Column('color', String(50)),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
    'purchase_order': [
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('order_id', String(100), unique=True, nullable=False, index=True),
        Column('supplier_id', String(100), index=True),
        Column('amount', Float),
        Column('quantity', Integer),
        Column('status', String(50)),
        Column('purchase_date', DateTime),
        Column('delivery_date', DateTime),
        Column('created_at', DateTime, default=sa.func.now()),
    ],
}


def init_database():
    """初始化数据库"""
    try:
        # 获取数据库连接
        credentials = DatabaseCredentials()
        connection_string = credentials.get_connection_string()
        engine = create_engine(connection_string)
        
        logger.info(f"连接到数据库：{connection_string.split('@')[1] if '@' in connection_string else 'local'}")
        
        # 创建所有表
        metadata = MetaData()
        
        for table_name, columns in TABLES_SCHEMA.items():
            Table(table_name, metadata, *columns)
            logger.info(f"定义表结构：{table_name}")
        
        # 创建表
        metadata.create_all(engine)
        logger.info("✅ 所有表创建成功！")
        
        # 验证表
        inspector = sa.inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print("\n" + "=" * 60)
        print("数据库初始化完成")
        print("=" * 60)
        print(f"创建表数量: {len(existing_tables)}")
        print("\n已创建的表:")
        for i, table in enumerate(existing_tables, 1):
            row_count = engine.execute(f"SELECT COUNT(*) FROM {table}").scalar()
            print(f"  {i:2d}. {table:25s} (0 条记录)")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败：{e}")
        return False


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
