# -*- coding: utf-8 -*-
"""
全局配置参数模块

本模块定义项目运行的全局配置参数，包括：
- 文件处理配置
- 数据库配置
- 清洗策略配置
- 性能优化参数
"""

import os
from typing import Dict, Any

# ============================================================
# 基础配置
# ============================================================

# 项目名称
PROJECT_NAME = "PythonDataClean"

# 项目版本
PROJECT_VERSION = "1.0.0"

# 运行模式：development、staging、production
RUN_MODE = os.getenv("RUN_MODE", "development")

# 是否调试模式
DEBUG = RUN_MODE == "development"

# ============================================================
# 文件处理配置
# ============================================================

# 临时数据存储根目录
TEMP_DATA_DIR = os.getenv("TEMP_DATA_DIR", "data/temp")

# 已处理数据记录目录
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")

# 清洗失败数据目录
FAILED_DATA_DIR = os.getenv("FAILED_DATA_DIR", "data/failed")

# 日志输出目录
LOG_DIR = os.getenv("LOG_DIR", "logs")

# 支持的数据格式
SUPPORTED_FILE_FORMATS = ["json", "csv", "jsonl", "parquet", "xml"]

# 最大文件大小限制（MB）
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5000"))

# ============================================================
# 数据库配置
# ============================================================

# 数据库类型
DB_TYPE = os.getenv("DB_TYPE", "mysql")

# 数据库主机
DB_HOST = os.getenv("DB_HOST", "localhost")

# 数据库端口
DB_PORT = int(os.getenv("DB_PORT", "3306"))

# 数据库名称
DB_NAME = os.getenv("DB_NAME", "data_clean")

# 数据库用户名
DB_USER = os.getenv("DB_USER", "root")

# 数据库密码
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# 数据库字符集
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# 连接池大小
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

# 连接池溢出大小
DB_POOL_OVERFLOW = int(os.getenv("DB_POOL_OVERFLOW", "20"))

# 数据库连接超时时间（秒）
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "30"))

# ============================================================
# 清洗策略配置
# ============================================================

# 批处理大小配置
BATCH_SIZE_SMALL = 1000
BATCH_SIZE_MEDIUM = 5000
BATCH_SIZE_LARGE = 10000

# 文件大小阈值（MB）
FILE_SIZE_SMALL_THRESHOLD = 10
FILE_SIZE_MEDIUM_THRESHOLD = 500

# 记录数阈值
RECORD_COUNT_SMALL_THRESHOLD = 10000
RECORD_COUNT_MEDIUM_THRESHOLD = 100000

# 是否启用并行处理
ENABLE_PARALLEL_PROCESSING = os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true"

# 最大并行工作数
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "4"))

# 处理超时时间（秒）
PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "300"))

# ============================================================
# 清洗规则配置
# ============================================================

# 元数据规则配置目录
METADATA_RULES_DIR = os.getenv("METADATA_RULES_DIR", "config/metadata_rules")

# 支持的业务类型
SUPPORTED_BUSINESS_TYPES = [
    "EC_GOODS_PHONE",          # 电商商品-手机
    "EC_GOODS_OTHER",          # 电商商品-其他
    "EC_COMMENT",              # 电商商品评论
    "SOCIAL_COMMENT",          # 社交平台评论
    "SOCIAL_POST",             # 社交平台帖子
    "NEWS_ARTICLE",            # 资讯文章
    "FINANCE_REPORT",          # 财务报表
    "ENTERPRISE_INFO",         # 企业工商信息
    "RECRUIT_JOB",             # 招聘岗位
    "VIDEO_METADATA",          # 短视频元数据
    "USER_PROFILE",            # 用户基础信息
    "PROPERTY_INFO",           # 房产信息
    "CAR_INFO",                # 汽车信息
    "PURCHASE_ORDER",          # 采购订单信息
    "CUSTOMER_DIALOG",         # 客户对话
]

# ============================================================
# 大模型API配置
# ============================================================

# 是否启用大模型清洗
ENABLE_LLM_CLEANING = os.getenv("ENABLE_LLM_CLEANING", "true").lower() == "true"

# 大模型API类型：openai、local
LLM_API_TYPE = os.getenv("LLM_API_TYPE", "openai")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# OpenAI API基础URL
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

# OpenAI模型名称
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# 大模型API超时时间（秒）
LLM_API_TIMEOUT = int(os.getenv("LLM_API_TIMEOUT", "60"))

# 大模型API重试次数
LLM_API_MAX_RETRIES = int(os.getenv("LLM_API_MAX_RETRIES", "3"))

# 大模型API请求批大小
LLM_API_BATCH_SIZE = int(os.getenv("LLM_API_BATCH_SIZE", "10"))

# ============================================================
# 日志配置
# ============================================================

# 日志级别：DEBUG、INFO、WARNING、ERROR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志格式
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

# 日志时间格式
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件最大大小（MB）
LOG_FILE_MAX_SIZE_MB = int(os.getenv("LOG_FILE_MAX_SIZE_MB", "100"))

# 日志文件备份数量
LOG_FILE_BACKUP_COUNT = int(os.getenv("LOG_FILE_BACKUP_COUNT", "10"))

# 日志保留天数
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

# ============================================================
# 编码配置
# ============================================================

# 强制使用UTF-8编码
FORCE_UTF8_ENCODING = True

# 默认编码
DEFAULT_ENCODING = "utf-8"

# ============================================================
# 数据质量配置
# ============================================================

# 数据质量评分阈值
QUALITY_SCORE_EXCELLENT = 85          # 优秀（可直接使用）
QUALITY_SCORE_GOOD = 70               # 良好（可使用但需标记）
QUALITY_SCORE_FAIR = 50               # 一般（需要审查）

# 缺失率阈值（核心字段）
MISSING_RATE_THRESHOLD_CORE = 0.1     # 10%

# 缺失率阈值（非核心字段）
MISSING_RATE_THRESHOLD_OPTIONAL = 0.5 # 50%

# ============================================================
# 数据存储配置
# ============================================================

# 按大小分层的存储策略
STORAGE_STRATEGY_CONFIG: Dict[str, Any] = {
    "small": {                  # <10万/年
        "strategy": "unified_table",
        "batch_size": BATCH_SIZE_SMALL,
        "enable_partition": False,
    },
    "medium": {                 # 10-100万/年
        "strategy": "business_type_independent_table",
        "batch_size": BATCH_SIZE_MEDIUM,
        "enable_partition": False,
    },
    "large": {                  # 100-1000万/年
        "strategy": "time_partitioned_table",
        "batch_size": BATCH_SIZE_LARGE,
        "partition_type": "month",
        "enable_partition": True,
    },
    "extra_large": {            # >1000万/年
        "strategy": "hash_partitioned_table",
        "batch_size": BATCH_SIZE_LARGE,
        "partition_type": "hash",
        "partition_count": 10,
        "enable_partition": True,
    }
}

# ============================================================
# 错误处理配置
# ============================================================

# 最大重试次数
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# 重试延迟（秒）
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "1"))

# 是否在遇到错误时继续处理其他文件
CONTINUE_ON_ERROR = os.getenv("CONTINUE_ON_ERROR", "true").lower() == "true"

# ============================================================
# 临时数据清理配置
# ============================================================

# 临时数据保留天数
TEMP_DATA_RETENTION_DAYS = int(os.getenv("TEMP_DATA_RETENTION_DAYS", "7"))

# 清洗成功后是否保留临时数据
KEEP_TEMP_DATA_AFTER_SUCCESS = os.getenv("KEEP_TEMP_DATA_AFTER_SUCCESS", "false").lower() == "true"

# 清洗失败的数据保留天数
FAILED_DATA_RETENTION_DAYS = int(os.getenv("FAILED_DATA_RETENTION_DAYS", "30"))

# ============================================================
# 阿里云配置（如果需要）
# ============================================================

# 阿里云访问Key
ALIYUN_ACCESS_KEY = os.getenv("ALIYUN_ACCESS_KEY", "")

# 阿里云访问Secret
ALIYUN_ACCESS_SECRET = os.getenv("ALIYUN_ACCESS_SECRET", "")

# 阿里云Bucket名称
ALIYUN_BUCKET_NAME = os.getenv("ALIYUN_BUCKET_NAME", "")

# 阿里云服务器地址
ALIYUN_OSS_ENDPOINT = os.getenv("ALIYUN_OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")

# ============================================================
# API服务配置
# ============================================================

# API服务主机
API_HOST = os.getenv("API_HOST", "0.0.0.0")

# API服务端口
API_PORT = int(os.getenv("API_PORT", "5000"))

# ============================================================
class Settings:
    """全局设置类"""
    
    # 基础
    PROJECT_NAME = PROJECT_NAME
    PROJECT_VERSION = PROJECT_VERSION
    DEBUG = DEBUG
    RUN_MODE = RUN_MODE
    
    # 文件
    TEMP_DATA_DIR = TEMP_DATA_DIR
    LOG_DIR = LOG_DIR
    MAX_FILE_SIZE_MB = MAX_FILE_SIZE_MB
    
    # 数据库
    DB_TYPE = DB_TYPE
    DB_HOST = DB_HOST
    DB_PORT = DB_PORT
    DB_NAME = DB_NAME
    DB_USER = DB_USER
    DB_PASSWORD = DB_PASSWORD
    
    # LLM
    LLM_API_KEY = OPENAI_API_KEY
    LLM_API_BASE = OPENAI_API_BASE
    LLM_MODEL = OPENAI_MODEL
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2000
    
    # API
    API_HOST = API_HOST
    API_PORT = API_PORT


# ============================================================
# 函数：获取配置
# ============================================================

def get_config_as_dict() -> Dict[str, Any]:
    """
    将所有配置参数转为字典
    
    Returns:
        包含所有配置的字典
    """
    config = {}
    for name, value in globals().items():
        # 跳过内置属性和函数
        if not name.startswith('_') and not callable(value) and name.isupper():
            config[name] = value
    return config


def get_storage_strategy_config(data_level: str) -> Dict[str, Any]:
    """
    获取指定数据规模的存储策略配置
    
    Args:
        data_level: 数据规模级别 (small/medium/large/extra_large)
    
    Returns:
        存储策略配置字典
    
    Raises:
        KeyError: 如果指定的数据级别不存在
    """
    if data_level not in STORAGE_STRATEGY_CONFIG:
        raise KeyError(f"不支持的数据规模级别：{data_level}")
    return STORAGE_STRATEGY_CONFIG[data_level].copy()
