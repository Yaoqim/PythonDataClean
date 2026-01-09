# -*- coding: utf-8 -*-
"""
监控模块初始化

集成Prometheus监控系统
"""

from src.monitoring.metrics import (
    start_metrics_server,
    track_cleaning,
    track_db_operation,
    track_http_request,
    REGISTRY,
    cleaning_requests_total,
    cleaning_records_processed,
    data_quality_score,
    deduplication_rate,
    missing_rate,
)

__all__ = [
    'start_metrics_server',
    'track_cleaning',
    'track_db_operation',
    'track_http_request',
    'REGISTRY',
    'cleaning_requests_total',
    'cleaning_records_processed',
    'data_quality_score',
    'deduplication_rate',
    'missing_rate',
]
