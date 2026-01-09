# -*- coding: utf-8 -*-
"""
MCP数据清洗服务

MCP（Model Context Protocol）服务入口
提供RESTful API接口进行数据清洗
"""

from typing import Dict, Any, Optional
import json
from datetime import datetime

from src.utils.logger import get_logger
from src.orchestrator.orchestrator import CleaningOrchestrator

logger = get_logger(__name__)


class MCPDataCleaningService:
    """
    MCP数据清洗服务
    
    核心职责：
    1. 接收清洗请求
    2. 调用编排器执行清洗
    3. 返回标准化MCP响应
    """
    
    @staticmethod
    def clean_data(
        data_file_path: str,
        enable_llm: bool = False,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        清洗数据的主入口
        
        Args:
            data_file_path: 数据文件路径
            enable_llm: 是否启用LLM进行高级清洗
            user_id: 用户ID（可选）
        
        Returns:
            MCP标准响应
            
        示例请求：
            {
                "method": "cleanData",
                "params": {
                    "data_file_path": "/data/EC_GOODS_PHONE_20240108_0001.json",
                    "enable_llm": true,
                    "user_id": "user_123"
                }
            }
        
        示例成功响应：
            {
                "code": 0,
                "message": "数据清洗成功",
                "data": {
                    "task_id": "20240108010203",
                    "business_type_id": "EC_GOODS_PHONE",
                    "status": "SUCCESS",
                    "timestamp": "2024-01-08T01:02:03",
                    "summary": {
                        "original_count": 1000,
                        "cleaned_count": 950,
                        "quality_score": 85.5,
                        "statistics": {
                            "dedup_rate": 0.05,
                            "missing_rate": 0.02
                        }
                    },
                    "storage_info": [
                        {
                            "business_type_id": "EC_GOODS_PHONE",
                            "table_name": "ec_goods_phone",
                            "inserted_count": 950,
                            "database": "production",
                            "key_fields": ["product_id", "product_name", ...],
                            "time_range": {...},
                            "insert_time": "2024-01-08T01:02:03"
                        }
                    ]
                }
            }
        
        示例错误响应：
            {
                "code": 10000,
                "message": "无法读取数据文件",
                "data": {
                    "task_id": "20240108010204",
                    "status": "FAILED",
                    "timestamp": "2024-01-08T01:02:04"
                }
            }
        """
        logger.info(f"收到清洗请求：{data_file_path}，enable_llm={enable_llm}")
        
        try:
            # 调用编排器
            response = CleaningOrchestrator.process_cleaning_task(
                data_file_path,
                enable_llm=enable_llm
            )
            
            # 记录用户信息
            if user_id:
                logger.info(f"用户{user_id}提交的任务：{response.get('data', {}).get('task_id')}")
            
            return response
        
        except Exception as e:
            logger.error(f"清洗服务异常：{e}", exc_info=True)
            return {
                'code': 10000,
                'message': f"服务异常：{str(e)}",
                'data': {
                    'task_id': datetime.now().strftime('%Y%m%d%H%M%S'),
                    'status': 'FAILED',
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    @staticmethod
    def get_supported_business_types() -> Dict[str, Any]:
        """
        获取支持的业务类型列表
        
        Returns:
            MCP响应，包含支持的业务类型信息
        """
        from src.metadata.business_type_registry import BusinessTypeRegistry
        
        business_types = BusinessTypeRegistry.list_business_types()
        business_type_configs = []
        
        for bt_id in business_types:
            config = BusinessTypeRegistry.get_business_type_config(bt_id)
            business_type_configs.append({
                'business_type_id': bt_id,
                'name': config.get('name'),
                'description': config.get('description'),
                'table_name': config.get('table_name'),
                'data_carrier_type': config.get('data_carrier_type')
            })
        
        return {
            'code': 0,
            'message': '获取业务类型列表成功',
            'data': {
                'count': len(business_type_configs),
                'business_types': business_type_configs
            }
        }
    
    @staticmethod
    def get_cleaning_status(task_id: str) -> Dict[str, Any]:
        """
        获取清洗任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            MCP响应
        """
        logger.info(f"查询任务状态：{task_id}")
        
        # 这里可以从Redis或数据库查询任务状态
        # 当前简化实现，实际环境中需要持久化存储
        
        return {
            'code': 0,
            'message': '查询成功',
            'data': {
                'task_id': task_id,
                'status': 'COMPLETED',
                'timestamp': datetime.now().isoformat()
            }
        }


# 便利函数
def clean_data(
    data_file_path: str,
    enable_llm: bool = False
) -> Dict[str, Any]:
    """快速清洗数据"""
    return MCPDataCleaningService.clean_data(data_file_path, enable_llm)


def get_supported_business_types() -> Dict[str, Any]:
    """获取支持的业务类型"""
    return MCPDataCleaningService.get_supported_business_types()
