# -*- coding: utf-8 -*-
"""
Flask REST API服务器

提供HTTP端点供客户端调用MCP服务
"""

from flask import Flask, request, jsonify
import os
import sys

# 添加项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import get_logger
from src.mcp_service import MCPDataCleaningService
from config import yaml_loader

logger = get_logger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'MCP Data Cleaning Service',
        'version': '1.0.0'
    })


@app.route('/api/v1/clean', methods=['POST'])
def clean_data():
    """
    数据清洗API端点
    
    Request JSON:
    {
        "data_file_path": "/path/to/data.json",
        "enable_llm": false,
        "user_id": "user_123"
    }
    
    Response:
    {
        "code": 0,
        "message": "数据清洗成功",
        "data": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 10000,
                'message': '请求体为空'
            }), 400
        
        data_file_path = data.get('data_file_path')
        enable_llm = data.get('enable_llm', False)
        user_id = data.get('user_id')
        
        if not data_file_path:
            return jsonify({
                'code': 10000,
                'message': '缺少必须参数：data_file_path'
            }), 400
        
        # 调用清洗服务
        response = MCPDataCleaningService.clean_data(
            data_file_path,
            enable_llm=enable_llm,
            user_id=user_id
        )
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"API处理失败：{e}", exc_info=True)
        return jsonify({
            'code': 10000,
            'message': f"服务异常：{str(e)}"
        }), 500


@app.route('/api/v1/business-types', methods=['GET'])
def get_business_types():
    """
    获取支持的业务类型
    
    Response:
    {
        "code": 0,
        "message": "获取业务类型列表成功",
        "data": {
            "count": 3,
            "business_types": [...]
        }
    }
    """
    try:
        response = MCPDataCleaningService.get_supported_business_types()
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"API处理失败：{e}", exc_info=True)
        return jsonify({
            'code': 10000,
            'message': f"服务异常：{str(e)}"
        }), 500


@app.route('/api/v1/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    获取任务状态
    
    Response:
    {
        "code": 0,
        "message": "查询成功",
        "data": {
            "task_id": "20240108010203",
            "status": "COMPLETED",
            "timestamp": "2024-01-08T01:02:03"
        }
    }
    """
    try:
        response = MCPDataCleaningService.get_cleaning_status(task_id)
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"API处理失败：{e}", exc_info=True)
        return jsonify({
            'code': 10000,
            'message': f"服务异常：{str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'code': 404,
        'message': '端点不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'code': 500,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    api_config = yaml_loader.get_api_config()
    app_config = yaml_loader.get("app")
    logger.info(f"启动MCP数据清洗服务，端口：{api_config.get('port')}")
    app.run(
        host=api_config.get('host', '0.0.0.0'),
        port=api_config.get('port', 5000),
        debug=app_config.get('debug', False),
        threaded=True
    )
