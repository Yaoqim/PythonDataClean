# -*- coding: utf-8 -*-
"""
MCP数据清洗服务 - 主程序入口

这是项目的主入口点，负责：
1. 初始化系统（数据库、日志等）
2. 启动清洗流程
3. 返回处理结果

执行方式：
python main.py [file1.json] [file2.json] ...

示例：
python main.py data/EC_GOODS_PHONE_20240108_0001.json
"""

import sys
import os
from pathlib import Path
from typing import List

# 添加项目根路径
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.logger import get_logger
from src.orchestrator.orchestrator import CleaningOrchestrator
from src.file_service.file_handler import FileHandler

logger = get_logger(__name__)


def main():
    """主程序入口"""
    
    logger.info("=" * 80)
    logger.info("MCP 数据清洗服务启动")
    logger.info("=" * 80)
    
    # 获取命令行参数
    if len(sys.argv) < 2:
        logger.error("错误：未指定文件路径")
        logger.info("用法：python main.py <文件路径> [文件路径2] ...")
        logger.info("示例：python main.py data/EC_GOODS_PHONE_20240108_0001.json")
        return 1
    
    # 收集所有文件路径
    file_paths: List[str] = sys.argv[1:]
    
    logger.info(f"待处理文件数：{len(file_paths)}")
    
    # 验证文件存在性
    valid_files = []
    for file_path in file_paths:
        # 支持本地文件和OSS路径
        file_exists = False
        if file_path.startswith(('oss://', '/aliyun/')):
            # OSS路径
            file_exists = FileHandler.check_file_exists(file_path)
        else:
            # 本地路径
            file_exists = os.path.exists(file_path)
        
        if not file_exists:
            logger.warning(f"文件不存在：{file_path}")
        else:
            valid_files.append(file_path)
            logger.info(f"文件有效：{file_path}")
    
    if not valid_files:
        logger.error("没有找到任何有效的文件")
        return 1
    
    # 执行清洗流程
    try:
        logger.info("开始处理数据...")
        
        # 逐个处理文件
        results = []
        for file_path in valid_files:
            logger.info(f"处理文件：{file_path}")
            result = CleaningOrchestrator.process_cleaning_task(file_path, enable_llm=False)
            
            # 转换结果格式
            if result.get('code') == 0:
                data = result.get('data', {})
                summary = data.get('summary', {})
                results.append({
                    'status': 'success',
                    'business_type': data.get('business_type_id'),
                    'original_count': summary.get('original_count', 0),
                    'cleaned_count': summary.get('cleaned_count', 0),
                    'stored_count': data.get('storage_info', [{}])[0].get('inserted_count', 0) if data.get('storage_info') else 0,
                    'table_name': data.get('storage_info', [{}])[0].get('table_name') if data.get('storage_info') else 'N/A',
                    'errors': []
                })
            else:
                results.append({
                    'status': 'failed',
                    'business_type': 'N/A',
                    'original_count': 0,
                    'cleaned_count': 0,
                    'stored_count': 0,
                    'table_name': 'N/A',
                    'errors': [result.get('message', '未知错误')]
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('status') == 'success')
        partial_count = sum(1 for r in results if r.get('status') == 'partial_success')
        failed_count = sum(1 for r in results if r.get('status') == 'failed')
        
        total_original = sum(r.get('original_count', 0) for r in results)
        total_cleaned = sum(r.get('cleaned_count', 0) for r in results)
        total_stored = sum(r.get('stored_count', 0) for r in results)
        
        # 输出最终结果
        logger.info("=" * 80)
        logger.info("处理完成 - 最终统计")
        logger.info("=" * 80)
        logger.info(f"文件总数：{len(results)}")
        logger.info(f"  成功：{success_count}")
        logger.info(f"  部分成功：{partial_count}")
        logger.info(f"  失败：{failed_count}")
        logger.info("")
        logger.info(f"数据统计：")
        logger.info(f"  原始记录数：{total_original}")
        logger.info(f"  清洗后记录数：{total_cleaned}")
        logger.info(f"  存储成功记录数：{total_stored}")
        logger.info("=" * 80)
        
        # 详细输出每个文件的结果
        logger.info("")
        logger.info("详细结果：")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. 文件处理结果")
            logger.info(f"   状态：{result.get('status')}")
            logger.info(f"   业务类型：{result.get('business_type', 'N/A')}")
            logger.info(f"   原始数：{result.get('original_count', 0)}")
            logger.info(f"   清洗数：{result.get('cleaned_count', 0)}")
            logger.info(f"   存储表：{result.get('table_name', 'N/A')}")
            
            if result.get('errors'):
                logger.warning(f"   错误信息：")
                for error in result.get('errors', []):
                    logger.warning(f"     - {error}")
        
        logger.info("=" * 80)
        
        # 返回退出码
        return 0 if failed_count == 0 else 1
        
    except Exception as e:
        logger.error(f"处理异常：{e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
