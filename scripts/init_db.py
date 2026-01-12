# -*- coding: utf-8 -*-
"""
数据库初始化脚本

仅为以下3个业务类型创建数据表：
1. 电商商品信息 (ec_product_info)
2. 电商商品评论 (ec_comment_YYYY)
3. 客户对话 (customer_conversation)

执行方式: python scripts/init_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from config.db_credentials import DatabaseCredentials
from sqlalchemy import create_engine, text, inspect

logger = get_logger(__name__)

# ============================================================
# SQL 创建表语句
# ============================================================

CREATE_TABLES_SQL = """
-- ============================================================
-- 1. 电商商品信息表
-- ============================================================
DROP TABLE IF EXISTS ec_product_info_tag;
DROP TABLE IF EXISTS ec_product_info;
CREATE TABLE ec_product_info (
  -- 基础主键
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
  
  -- 枢纽字段
  `knowledge_id` BIGINT COMMENT '全局唯一知识ID (关联自knowledge_index表)',
  `product_id` VARCHAR(100) NOT NULL COMMENT '商品原始唯一标识符',
  `source_platform` VARCHAR(20) NOT NULL COMMENT '来源平台(jd/taobao/suning/pdd)',
  
  -- 业务核心字段(五个核心字段)
  `title` VARCHAR(200) NOT NULL COMMENT '商品标题',
  `price` DECIMAL(12, 2) NOT NULL COMMENT '现价/售价(已转RMB)',
  `currency_code` VARCHAR(3) NOT NULL DEFAULT 'CNY' COMMENT '原始货币代码',
  `shop_name` VARCHAR(100) NOT NULL DEFAULT '未知' COMMENT '店铺名称',
  
  -- 业务核心字段准确度评估（title）
  `title_anal` INT CHECK(title_anal >= 0 AND title_anal <= 100) COMMENT '商品标题准确度评分(0-100)',
  `title_anal_info` VARCHAR(500) COMMENT '商品标题准确度评估详细说明(含来源、一致性、验证详情)',
  
  -- 业务核心字段准确度评估（price）
  `price_anal` INT CHECK(price_anal >= 0 AND price_anal <= 100) COMMENT '价格准确度评分(0-100)',
  `price_anal_info` VARCHAR(500) COMMENT '价格准确度评估详细说明(含来源、一致性、验证详情)',
  
  -- 业务核心字段准确度评估（currency_code）
  `currency_code_anal` INT CHECK(currency_code_anal >= 0 AND currency_code_anal <= 100) COMMENT '货币代码准确度评分(0-100)',
  `currency_code_anal_info` VARCHAR(500) COMMENT '货币代码准确度评估详细说明(含来源、一致性、验证详情)',
  
  -- 业务核心字段准确度评估（shop_name）
  `shop_name_anal` INT CHECK(shop_name_anal >= 0 AND shop_name_anal <= 100) COMMENT '店铺名准确度评分(0-100)',
  `shop_name_anal_info` VARCHAR(500) COMMENT '店铺名准确度评估详细说明(含来源、一致性、验证详情)',
  
  -- 业务核心字段准确度评估（source_platform）
  `source_platform_anal` INT CHECK(source_platform_anal >= 0 AND source_platform_anal <= 100) COMMENT '来源平台准确度评分(0-100)',
  `source_platform_anal_info` VARCHAR(500) COMMENT '来源平台准确度评估详细说明(含来源、一致性、验证详情)',
  
  -- 其他业务字段
  `original_price` DECIMAL(12, 2) COMMENT '原价/市场指导价',
  `brand` VARCHAR(100) COMMENT '品牌名称(标准化)',
  `spec_params` JSON COMMENT '规格参数(JSON格式)',
  `sales_volume` BIGINT COMMENT '销量(整数)',
  `comment_count` BIGINT COMMENT '评论数',
  `rating` DECIMAL(2, 1) COMMENT '平均评分(0-5)',
  `good_rate` DECIMAL(5, 2) COMMENT '好评率(0-100%)',
  `shop_id` VARCHAR(100) COMMENT '店铺唯一标识',
  `is_official` TINYINT(1) DEFAULT 0 COMMENT '是否官方旗舰店(0/1)',
  `listing_time` DATETIME COMMENT '商品上架时间',
  `update_time` DATETIME COMMENT '商品更新时间',
  
  -- 数据清洗标记字段
  `is_cleaned` TINYINT(1) DEFAULT 0 COMMENT '是否已清洗(0/1)',
  `abnormal_tag` VARCHAR(100) DEFAULT 'normal' COMMENT '异常标记',
  `spec_completeness` TINYINT(3) COMMENT '规格完整度评分(0-100%)',
  `data_source` VARCHAR(50) COMMENT '数据来源追踪',
  `clean_time` DATETIME COMMENT '清洗完成时间',
  
  -- 价格转换信息
  `price_currency_info` JSON COMMENT '完整价格转换信息',
  `is_price_converted` TINYINT(1) DEFAULT 0 COMMENT '是否已进行汇率转换',
  
  -- 公共必填字段
  `data_crawl_date` DATE NOT NULL COMMENT '数据抓取日期',
  `last_updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `is_valid` TINYINT(1) DEFAULT 1 COMMENT '记录有效性标记',
  `quality_score` DECIMAL(5, 2) COMMENT '数据质量评分',
  `data_status` VARCHAR(20) DEFAULT 'normal' COMMENT '数据处理状态',
  `version` INT DEFAULT 1 COMMENT '数据版本号',
  `tag_confidence` TINYINT(3) COMMENT '标签置信度',
  
  -- 索引
  UNIQUE KEY idx_platform_product (source_platform, product_id),
  KEY idx_knowledge_id (knowledge_id),
  KEY idx_brand_platform_time (brand, source_platform, listing_time),
  KEY idx_product_id_time (product_id, update_time),
  KEY idx_shop_name (shop_name),
  KEY idx_source_platform (source_platform),
  KEY idx_source_platform_anal (source_platform_anal),
  KEY idx_title_anal (title_anal),
  KEY idx_price_anal (price_anal),
  KEY idx_quality_score (quality_score),
  
  CONSTRAINT check_rating CHECK (rating >= 0 AND rating <= 5),
  CONSTRAINT check_good_rate CHECK (good_rate >= 0 AND good_rate <= 100),
  CONSTRAINT check_spec_completeness CHECK (spec_completeness >= 0 AND spec_completeness <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电商商品信息表';

-- ============================================================
-- 2. 电商商品标签表
-- ============================================================
CREATE TABLE IF NOT EXISTS ec_product_info_tag (
  -- 主键
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
  
  -- 关联字段
  `product_record_id` BIGINT NOT NULL COMMENT '对应ec_product_info表的id',
  `knowledge_id` BIGINT COMMENT '全局唯一知识ID',
  `tag_value` VARCHAR(100) NOT NULL COMMENT '标签值',
  
  -- 标签置信度
  `tag_confidence` INT NOT NULL COMMENT '标签置信度(0-100)',
  
  -- 元数据
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '标签创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '标签更新时间',
  
  -- 索引和外键
  FOREIGN KEY (`product_record_id`) REFERENCES `ec_product_info`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  KEY idx_knowledge_id (knowledge_id),
  KEY idx_tag_value (`tag_value`),
  KEY idx_confidence (`tag_confidence`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电商商品标签表';

-- ============================================================
-- 3. 电商商品评论表(按年分片 2024)
-- ============================================================
DROP TABLE IF EXISTS ec_comment_2024;
CREATE TABLE ec_comment_2024 (
    -- 基础主键
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    
    -- 核心业务字段及其准确度评估
    comment_id VARCHAR(100) NOT NULL COMMENT '评论全局唯一ID',
    product_id VARCHAR(50) NOT NULL COMMENT '关联商品ID',
    product_id_anal INT CHECK(product_id_anal >= 0 AND product_id_anal <= 100) COMMENT '商品ID准确度评分(0-100)',
    product_id_anal_info VARCHAR(500) COMMENT '商品ID准确度评估说明',
    
    user_name VARCHAR(100) NOT NULL COMMENT '用户名称(脱敏)',
    user_name_anal INT CHECK(user_name_anal >= 0 AND user_name_anal <= 100) COMMENT '用户名准确度评分(0-100)',
    user_name_anal_info VARCHAR(500) COMMENT '用户名准确度评估说明',
    
    comment_content LONGTEXT NOT NULL COMMENT '评论内容(清洁后≤10000字)',
    comment_content_anal INT CHECK(comment_content_anal >= 0 AND comment_content_anal <= 100) COMMENT '评论内容准确度评分(0-100)',
    comment_content_anal_info VARCHAR(500) COMMENT '评论内容准确度评估说明',
    
    rating_score FLOAT COMMENT '评分(1-5,仅一级评论)',
    rating_score_anal INT CHECK(rating_score_anal >= 0 AND rating_score_anal <= 100) COMMENT '评分准确度评分(0-100)',
    rating_score_anal_info VARCHAR(500) COMMENT '评分准确度评估说明',
    
    comment_date DATETIME NOT NULL COMMENT '评论发布时间(YYYY-MM-DD HH:MM:SS)',
    comment_date_anal INT CHECK(comment_date_anal >= 0 AND comment_date_anal <= 100) COMMENT '评论时间准确度评分(0-100)',
    comment_date_anal_info VARCHAR(500) COMMENT '评论时间准确度评估说明',
    
    comment_level INT NOT NULL CHECK(comment_level IN (1, 2)) COMMENT '评论层级(1=一级,2=二级)',
    comment_level_anal INT CHECK(comment_level_anal >= 0 AND comment_level_anal <= 100) COMMENT '层级准确度评分(0-100)',
    comment_level_anal_info VARCHAR(500) COMMENT '层级准确度评估说明',
    
    parent_comment_id VARCHAR(100) COMMENT '父评论ID(仅二级评论)',
    parent_comment_id_anal INT CHECK(parent_comment_id_anal >= 0 AND parent_comment_id_anal <= 100) COMMENT '父评论ID准确度评分(0-100)',
    parent_comment_id_anal_info VARCHAR(500) COMMENT '父评论ID准确度评估说明',
    
    comment_id_anal INT CHECK(comment_id_anal >= 0 AND comment_id_anal <= 100) COMMENT '评论ID准确度评分(0-100)',
    comment_id_anal_info VARCHAR(500) COMMENT '评论ID准确度评估说明',
    
    -- 补充字段
    is_verified INT DEFAULT 0 CHECK(is_verified IN (0, 1)) COMMENT '是否认证购买(0=否,1=是)',
    is_spam INT DEFAULT 0 CHECK(is_spam IN (0, 1)) COMMENT '是否垃圾评论(0=否,1=是)',
    helpful_count INT CHECK(helpful_count >= 0 AND helpful_count < 1000000) COMMENT '有用数/点赞数',
    helpful_count_anal INT CHECK(helpful_count_anal >= 0 AND helpful_count_anal <= 100) COMMENT '有用数准确度评分(0-100)',
    helpful_count_anal_info VARCHAR(500) COMMENT '有用数准确度评估说明',
    
    -- 时间字段
    data_crawl_date DATE NOT NULL COMMENT '数据抓取日期',
    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '清洗完成时间',
    imported_at TIMESTAMP COMMENT '数据导入数据库时间',
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    -- 有效性字段
    is_valid BOOLEAN DEFAULT TRUE COMMENT '数据是否有效',
    quality_score INT CHECK(quality_score >= 0 AND quality_score <= 100) COMMENT '数据质量评分(0-100)',
    data_status ENUM('valid', 'pending_review', 'invalid') DEFAULT 'valid' COMMENT '数据处理状态',
    validity_reason VARCHAR(500) COMMENT '无效原因说明',
    
    -- 版本控制
    version INT DEFAULT 1 COMMENT '数据版本号',
    
    -- 索引
    UNIQUE KEY idx_comment_id (comment_id),
    KEY idx_product_id (product_id),
    KEY idx_user_name (user_name),
    KEY idx_comment_level (comment_level),
    KEY idx_parent_comment_id (parent_comment_id),
    KEY idx_rating_score (rating_score),
    KEY idx_comment_date (comment_date),
    KEY idx_crawl_date (data_crawl_date),
    KEY idx_data_status (data_status),
    KEY idx_quality_score (quality_score),
    KEY idx_is_spam (is_spam),
    KEY idx_is_verified (is_verified)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电商商品评论表(2024年)';

-- ============================================================
-- 4. 客户对话表
-- ============================================================
DROP TABLE IF EXISTS customer_conversation_tag;
DROP TABLE IF EXISTS customer_conversation;
CREATE TABLE customer_conversation (
    -- 基础主键
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    
    -- 核心业务字段
    conversation_id VARCHAR(100) NOT NULL COMMENT '对话唯一ID',
    customer_name VARCHAR(50) NOT NULL COMMENT '客户名称(脱敏)',
    customer_name_anal INT CHECK(customer_name_anal >= 0 AND customer_name_anal <= 100) COMMENT '客户名准确度评分(0-100)',
    customer_name_anal_info VARCHAR(500) COMMENT '客户名准确度评估说明',
    
    agent_name VARCHAR(30) COMMENT '客服名称',
    agent_name_anal INT CHECK(agent_name_anal >= 0 AND agent_name_anal <= 100) COMMENT '客服名准确度评分(0-100)',
    agent_name_anal_info VARCHAR(500) COMMENT '客服名准确度评估说明',
    
    message_type VARCHAR(50) NOT NULL COMMENT '消息类型(客户消息/客服回复/系统消息/转移通知/其他)',
    message_type_anal INT CHECK(message_type_anal >= 0 AND message_type_anal <= 100) COMMENT '消息类型准确度评分(0-100)',
    message_type_anal_info VARCHAR(500) COMMENT '消息类型准确度评估说明',
    
    message_content LONGTEXT NOT NULL COMMENT '消息内容(清洁后≤5000字)',
    message_content_anal INT CHECK(message_content_anal >= 0 AND message_content_anal <= 100) COMMENT '消息内容准确度评分(0-100)',
    message_content_anal_info VARCHAR(500) COMMENT '消息内容准确度评估说明',
    
    message_time DATETIME NOT NULL COMMENT '消息时间(YYYY-MM-DD HH:MM:SS)',
    message_time_anal INT CHECK(message_time_anal >= 0 AND message_time_anal <= 100) COMMENT '消息时间准确度评分(0-100)',
    message_time_anal_info VARCHAR(500) COMMENT '消息时间准确度评估说明',
    
    platform VARCHAR(50) NOT NULL COMMENT '平台(微信/淘宝/企业QQ/钉钉/客服热线/邮件/其他)',
    platform_anal INT CHECK(platform_anal >= 0 AND platform_anal <= 100) COMMENT '平台准确度评分(0-100)',
    platform_anal_info VARCHAR(500) COMMENT '平台准确度评估说明',
    
    -- 非核心业务字段
    user_id VARCHAR(100) COMMENT '用户ID(脱敏)',
    conversation_topic VARCHAR(100) COMMENT '对话主题(关联标签表)',
    sentiment VARCHAR(50) COMMENT '情感倾向(正面/中立/负面)',
    conversation_status VARCHAR(50) COMMENT '对话状态(进行中/已结束/已转移/等待中)',
    resolution_time INT COMMENT '解决时长(分钟)',
    satisfaction INT CHECK(satisfaction >= 1 AND satisfaction <= 5) COMMENT '满意度(1-5)',
    
    -- 时间字段
    data_crawl_date DATE NOT NULL COMMENT '数据抓取日期',
    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '清洗完成时间',
    imported_at TIMESTAMP COMMENT '数据导入时间',
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    -- 有效性字段
    is_valid BOOLEAN DEFAULT TRUE COMMENT '数据是否有效',
    quality_score INT CHECK(quality_score >= 0 AND quality_score <= 100) COMMENT '数据质量评分(0-100)',
    data_status ENUM('valid', 'pending_review', 'invalid') DEFAULT 'valid' COMMENT '数据处理状态',
    validity_reason VARCHAR(500) COMMENT '无效原因说明',
    
    -- 版本控制
    version INT DEFAULT 1 COMMENT '数据版本号',
    
    -- 索引
    UNIQUE KEY idx_conversation_id (conversation_id),
    KEY idx_customer_name (customer_name),
    KEY idx_user_id (user_id),
    KEY idx_agent_name (agent_name),
    KEY idx_platform (platform),
    KEY idx_message_type (message_type),
    KEY idx_conversation_topic (conversation_topic),
    KEY idx_sentiment (sentiment),
    KEY idx_conversation_status (conversation_status),
    KEY idx_message_time (message_time),
    KEY idx_crawl_date (data_crawl_date),
    KEY idx_quality_score (quality_score),
    KEY idx_data_status (data_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户对话表';

-- ============================================================
-- 5. 客户对话标签表
-- ============================================================
CREATE TABLE customer_conversation_tag (
    -- 主键
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    
    -- 关联字段
    `conversation_record_id` BIGINT NOT NULL COMMENT '对应customer_conversation表的id',
    `conversation_id` VARCHAR(100) NOT NULL COMMENT '对话ID',
    `tag_value` VARCHAR(100) NOT NULL COMMENT '标签值',
    `tag_confidence` INT NOT NULL COMMENT '标签置信度(0-100)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '标签创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '标签更新时间',
    
    FOREIGN KEY (conversation_record_id) REFERENCES customer_conversation(id) ON DELETE CASCADE ON UPDATE CASCADE,
    KEY idx_conversation_id (conversation_id),
    KEY idx_tag_value (tag_value),
    KEY idx_confidence (tag_confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户对话标签表';
"""


def init_database():
    """初始化数据库"""
    try:
        # 获取数据库连接
        credentials = DatabaseCredentials()
        connection_string = credentials.get_connection_string()
        engine = create_engine(connection_string)
        
        logger.info(f"连接到数据库：{connection_string.split('@')[1] if '@' in connection_string else 'local'}")
        
        # 分割SQL语句并逐条执行
        # 使用分号分割，但要避免在字符串中的分号
        sql_statements = []
        current_statement = ""
        
        for line in CREATE_TABLES_SQL.split('\n'):
            current_statement += line + "\n"
            if line.strip().endswith(';'):
                sql_statements.append(current_statement.strip())
                current_statement = ""
        
        # 执行每条SQL语句
        with engine.connect() as connection:
            for sql_statement in sql_statements:
                if sql_statement.strip():
                    logger.debug(f"执行SQL语句...")
                    connection.execute(text(sql_statement))
            connection.commit()
        
        logger.info("[OK] 所有表创建成功！")
        
        # 验证表
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print("\n" + "=" * 80)
        print("数据库初始化完成")
        print("=" * 80)
        print(f"创建表数量: {len(existing_tables)}")
        print("\n已创建的表:")
        for i, table in enumerate(existing_tables, 1):
            print(f"  {i:2d}. {table}")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] 数据库初始化失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
