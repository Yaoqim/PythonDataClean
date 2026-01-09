# -*- coding: utf-8 -*-
"""
监控和指标收集系统

使用Prometheus进行指标收集和Grafana进行可视化
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, start_http_server
import time
from functools import wraps
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 创建独立的注册表
REGISTRY = CollectorRegistry()

# ============================================================
# 清洗相关指标
# ============================================================

# 清洗请求计数
cleaning_requests_total = Counter(
    'cleaning_requests_total',
    '清洗请求总数',
    ['business_type_id', 'status'],
    registry=REGISTRY
)

# 清洗耗时直方图
cleaning_duration_seconds = Histogram(
    'cleaning_duration_seconds',
    '单次清洗耗时（秒）',
    ['business_type_id'],
    registry=REGISTRY,
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
)

# 清洗吞吐量
cleaning_throughput = Gauge(
    'cleaning_throughput_records_per_second',
    '清洗吞吐量（条/秒）',
    ['business_type_id'],
    registry=REGISTRY
)

# 清洗记录数
cleaning_records_processed = Counter(
    'cleaning_records_processed_total',
    '已清洗的记录总数',
    ['business_type_id', 'status'],
    registry=REGISTRY
)

# ============================================================
# 数据质量指标
# ============================================================

# 数据质量评分
data_quality_score = Gauge(
    'data_quality_score',
    '数据质量评分',
    ['business_type_id'],
    registry=REGISTRY
)

# 去重率
deduplication_rate = Gauge(
    'deduplication_rate',
    '去重率',
    ['business_type_id'],
    registry=REGISTRY
)

# 缺失率
missing_rate = Gauge(
    'missing_rate',
    '缺失率',
    ['business_type_id'],
    registry=REGISTRY
)

# ============================================================
# 数据库相关指标
# ============================================================

# 数据库操作耗时
db_operation_duration_seconds = Histogram(
    'db_operation_duration_seconds',
    '数据库操作耗时（秒）',
    ['operation', 'status'],
    registry=REGISTRY,
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

# 数据库入库记录数
db_records_inserted_total = Counter(
    'db_records_inserted_total',
    '入库的记录总数',
    ['table_name', 'status'],
    registry=REGISTRY
)

# 数据库连接池状态
db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    '数据库连接池大小',
    registry=REGISTRY
)

db_active_connections = Gauge(
    'db_active_connections',
    '活跃数据库连接数',
    registry=REGISTRY
)

# ============================================================
# API 相关指标
# ============================================================

# HTTP 请求计数
http_requests_total = Counter(
    'http_requests_total',
    'HTTP 请求总数',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

# HTTP 请求耗时
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP 请求耗时（秒）',
    ['method', 'endpoint'],
    registry=REGISTRY,
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0)
)

# ============================================================
# 系统资源指标
# ============================================================

# 内存使用
memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    '内存使用量（字节）',
    registry=REGISTRY
)

# CPU使用率
cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU使用率（%）',
    registry=REGISTRY
)


# ============================================================
# 装饰器
# ============================================================

def track_cleaning(business_type_id: str):
    """装饰器：追踪清洗操作"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 记录成功
                cleaning_requests_total.labels(
                    business_type_id=business_type_id,
                    status='success'
                ).inc()
                
                cleaning_duration_seconds.labels(
                    business_type_id=business_type_id
                ).observe(duration)
                
                if 'original_count' in result and 'cleaned_count' in result:
                    records_count = result['cleaned_count']
                    throughput = records_count / duration if duration > 0 else 0
                    
                    cleaning_throughput.labels(
                        business_type_id=business_type_id
                    ).set(throughput)
                    
                    cleaning_records_processed.labels(
                        business_type_id=business_type_id,
                        status='success'
                    ).inc(records_count)
                    
                    # 记录质量指标
                    if 'statistics' in result:
                        stats = result['statistics']
                        deduplication_rate.labels(
                            business_type_id=business_type_id
                        ).set(stats.get('dedup_rate', 0))
                        
                        missing_rate.labels(
                            business_type_id=business_type_id
                        ).set(stats.get('missing_rate', 0))
                
                return result
            
            except Exception as e:
                cleaning_requests_total.labels(
                    business_type_id=business_type_id,
                    status='failed'
                ).inc()
                raise
        
        return wrapper
    return decorator


def track_db_operation(operation: str):
    """装饰器：追踪数据库操作"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                db_operation_duration_seconds.labels(
                    operation=operation,
                    status='success'
                ).observe(duration)
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                db_operation_duration_seconds.labels(
                    operation=operation,
                    status='failed'
                ).observe(duration)
                raise
        
        return wrapper
    return decorator


def track_http_request(method: str, endpoint: str):
    """装饰器：追踪 HTTP 请求"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status='success'
                ).inc()
                
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status='failed'
                ).inc()
                raise
        
        return wrapper
    return decorator


def start_metrics_server(port: int = 8000):
    """启动Prometheus指标服务器"""
    try:
        start_http_server(port, registry=REGISTRY)
        logger.info(f"✅ Prometheus 指标服务器启动成功（端口：{port}）")
    except Exception as e:
        logger.error(f"Prometheus 指标服务器启动失败：{e}")


if __name__ == '__main__':
    # 测试
    start_metrics_server(8000)
    
    # 模拟一些指标
    cleaning_requests_total.labels(business_type_id='EC_GOODS_PHONE', status='success').inc(5)
    cleaning_records_processed.labels(business_type_id='EC_GOODS_PHONE', status='success').inc(1000)
    
    print("✅ 监控系统启动成功")
    print("Prometheus 端点: http://localhost:8000/metrics")
