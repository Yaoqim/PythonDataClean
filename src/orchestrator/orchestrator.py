# -*- coding: utf-8 -*-
"""
数据清洗流程编排模块

负责协调整个清洗业务流程：
1. 文件获取
2. 元数据处理
3. Python清洗
4. 大模型清洗（可选）
5. 结果入库
6. 响应生成
"""

from typing import Dict, Any, Optional, List
import datetime

from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler
from src.file_service.file_handler import FileHandler
from src.file_service.metadata_loader import MetadataLoader
from src.metadata.metadata_validator import MetadataValidator
from src.metadata.business_type_registry import BusinessTypeRegistry
from src.db_service.db_manager import DatabaseManager
from src.business_cleaner.ec_goods_phone_cleaner import ECGoodsPhoneCleaner
from src.business_cleaner.ec_comment_cleaner import ECCommentCleaner
from src.business_cleaner.customer_dialog_cleaner import CustomerDialogCleaner
from src.business_cleaner.social_comment_cleaner import SocialCommentCleaner
from src.business_cleaner.social_post_cleaner import SocialPostCleaner
from src.business_cleaner.news_article_cleaner import NewsArticleCleaner
from src.business_cleaner.finance_report_cleaner import FinanceReportCleaner
from src.business_cleaner.enterprise_info_cleaner import EnterpriseInfoCleaner
from src.business_cleaner.recruit_job_cleaner import RecruitJobCleaner
from src.business_cleaner.video_metadata_cleaner import VideoMetadataCleaner
from src.business_cleaner.user_profile_cleaner import UserProfileCleaner
from src.business_cleaner.property_info_cleaner import PropertyInfoCleaner
from src.business_cleaner.car_info_cleaner import CarInfoCleaner
from src.business_cleaner.purchase_order_cleaner import PurchaseOrderCleaner

logger = get_logger(__name__)


class CleaningOrchestrator:
    """
    数据清洗流程编排器
    
    负责：
    1. 调度各个清洗步骤
    2. 错误处理和恢复
    3. 结果汇总和报告
    """
    
    # 清洗器映射
    CLEANERS = {
        'EC_GOODS_PHONE': ECGoodsPhoneCleaner,
        'EC_COMMENT': ECCommentCleaner,
        'CUSTOMER_DIALOG': CustomerDialogCleaner,
        'SOCIAL_COMMENT': SocialCommentCleaner,
        'SOCIAL_POST': SocialPostCleaner,
        'NEWS_ARTICLE': NewsArticleCleaner,
        'FINANCE_REPORT': FinanceReportCleaner,
        'ENTERPRISE_INFO': EnterpriseInfoCleaner,
        'RECRUIT_JOB': RecruitJobCleaner,
        'VIDEO_METADATA': VideoMetadataCleaner,
        'USER_PROFILE': UserProfileCleaner,
        'PROPERTY_INFO': PropertyInfoCleaner,
        'CAR_INFO': CarInfoCleaner,
        'PURCHASE_ORDER': PurchaseOrderCleaner,
    }
    
    @staticmethod
    def process_cleaning_task(
        data_file_path: str,
        enable_llm: bool = False
    ) -> Dict[str, Any]:
        """
        执行完整清洗流程
        
        Args:
            data_file_path: 数据文件路径
            enable_llm: 是否启用LLM清洗
        
        Returns:
            MCP响应字典
        """
        logger.info(f"开始清洗流程：{data_file_path}")
        
        task_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        
        try:
            # 第1步：文件获取
            logger.info("第1步：获取数据文件...")
            from src.file_service.file_handler import load_json_file, load_csv_file
            
            file_format = FileHandler.get_file_format(data_file_path)
            if file_format == '.json' or file_format == '.jsonl':
                records = load_json_file(data_file_path)
            elif file_format == '.csv':
                records = load_csv_file(data_file_path)
            else:
                return CleaningOrchestrator._build_error_response(
                    f"不支持的文件格式：{file_format}",
                    task_id
                )
            
            if not records:
                return CleaningOrchestrator._build_error_response(
                    f"无法读取数据文件：{data_file_path}",
                    task_id
                )
            
            logger.info(f"成功读取{len(records)}条记录")
            
            # 第2步：元数据处理
            logger.info("第2步：加载和验证元数据...")
            metadata_path = MetadataLoader.find_metadata_file(data_file_path)
            if not metadata_path:
                return CleaningOrchestrator._build_error_response(
                    f"无法找到元数据文件：{data_file_path}",
                    task_id
                )
            
            metadata = MetadataLoader.load_metadata(metadata_path)
            if not metadata:
                return CleaningOrchestrator._build_error_response(
                    f"无法加载元数据：{metadata_path}",
                    task_id
                )
            
            # 验证元数据必需字段
            missing_fields = MetadataLoader.REQUIRED_FIELDS - set(metadata.keys())
            if missing_fields:
                return CleaningOrchestrator._build_error_response(
                    f"元数据缺失必需字段：{missing_fields}",
                    task_id
                )
            
            business_type_id = metadata.get('business_type_id')
            logger.info(f"业务类型：{business_type_id}")
            
            # 第3步：业务类型特定清洗
            logger.info("第3步：执行业务清洗...")
            cleaner = CleaningOrchestrator.CLEANERS.get(business_type_id)
            if not cleaner:
                return CleaningOrchestrator._build_error_response(
                    f"不支持的业务类型：{business_type_id}",
                    task_id
                )
            
            # 调用相应的清洗器（统一接口）
            cleaning_result = cleaner.clean(records, enable_llm=enable_llm)
            
            if not cleaning_result.get('success'):
                return CleaningOrchestrator._build_error_response(
                    f"清洗失败：{cleaning_result.get('error')}",
                    task_id
                )
            
            logger.info(f"清洗完成：{cleaning_result['cleaned_count']}条记录")
            
            # 第4步：结果入库
            logger.info("第4步：入库...")
            from src.metadata.business_type_registry import BusinessTypeRegistry
            db_manager = DatabaseManager()
            
            table_name = BusinessTypeRegistry.get_table_name(business_type_id)
            if not table_name:
                logger.warning(f"业务类型{business_type_id}无对应的表配置")
                storage_info = {'success': False, 'error': '无表配置'}
            else:
                success_count, failed_count = db_manager.insert_records(
                    table_name,
                    cleaning_result['records']
                )
                storage_info = {
                    'success': failed_count == 0,
                    'table_name': table_name,
                    'inserted_count': success_count,
                    'failed_count': failed_count,
                    'database': 'production',
                    'error': f"失败{failed_count}条" if failed_count > 0 else None
                }
            
            if not storage_info.get('success'):
                logger.warning(f"数据入库失败：{storage_info.get('error')}")
                # 即使入库失败，也返回清洗成功的结果（数据可临时保存）
            
            # 第5步：生成响应
            logger.info("第5步：生成响应...")
            response = CleaningOrchestrator._build_success_response(
                task_id,
                business_type_id,
                cleaning_result,
                storage_info,
                metadata
            )
            
            logger.info(f"清洗流程完成：task_id={task_id}")
            return response
        
        except Exception as e:
            logger.error(f"清洗流程异常：{e}", exc_info=True)
            return CleaningOrchestrator._build_error_response(str(e), task_id)
    
    @staticmethod
    def _build_success_response(
        task_id: str,
        business_type_id: str,
        cleaning_result: Dict[str, Any],
        storage_info: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构建成功响应
        
        Args:
            task_id: 任务ID
            business_type_id: 业务类型ID
            cleaning_result: 清洗结果
            storage_info: 存储信息
            metadata: 元数据
        
        Returns:
            MCP成功响应
        """
        return {
            'code': 0,
            'message': '数据清洗成功',
            'data': {
                'task_id': task_id,
                'business_type_id': business_type_id,
                'status': 'SUCCESS',
                'timestamp': datetime.datetime.now().isoformat(),
                'summary': {
                    'original_count': cleaning_result['original_count'],
                    'cleaned_count': cleaning_result['cleaned_count'],
                    'quality_score': CleaningOrchestrator._calculate_quality_score(cleaning_result),
                    'statistics': cleaning_result.get('statistics', {})
                },
                'storage_info': [
                    {
                        'business_type_id': business_type_id,
                        'table_name': storage_info.get('table_name'),
                        'inserted_count': storage_info.get('inserted_count'),
                        'failed_count': storage_info.get('failed_count'),
                        'database': storage_info.get('database'),
                        'key_fields': storage_info.get('key_fields'),
                        'time_range': storage_info.get('time_range'),
                        'insert_time': storage_info.get('insert_time')
                    }
                ]
            }
        }
    
    @staticmethod
    def _build_error_response(
        error_message: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        构建错误响应
        
        Args:
            error_message: 错误消息
            task_id: 任务ID
        
        Returns:
            MCP错误响应
        """
        return {
            'code': 10000,
            'message': error_message,
            'data': {
                'task_id': task_id,
                'status': 'FAILED',
                'timestamp': datetime.datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def _calculate_quality_score(cleaning_result: Dict[str, Any]) -> float:
        """
        计算数据质量分数
        
        Args:
            cleaning_result: 清洗结果
        
        Returns:
            0-100的质量分数
        """
        # 基础分数
        base_score = 100
        
        # 去重率影响（满分40分）
        dedup_rate = cleaning_result.get('statistics', {}).get('dedup_rate', 0)
        dedup_score = 40 * (1 - dedup_rate)  # 去重率越高，扣分越多
        
        # 缺失率影响（满分30分）
        missing_rate = cleaning_result.get('statistics', {}).get('missing_rate', 0)
        missing_score = 30 * (1 - missing_rate)
        
        # 清洗完整率影响（满分30分）
        if cleaning_result['original_count'] > 0:
            clean_rate = cleaning_result['cleaned_count'] / cleaning_result['original_count']
            clean_score = 30 * clean_rate
        else:
            clean_score = 0
        
        quality_score = base_score - (40 - dedup_score) - (30 - missing_score) + (clean_score - 30)
        return max(0, min(100, quality_score))
