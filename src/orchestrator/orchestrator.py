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
            # 第1步：文件信息获取与元数据加载
            logger.info("第1步：获取文件信息与元数据...")
            from src.file_service.file_handler import load_json_file, load_csv_file, load_excel_file
            
            file_format = FileHandler.get_file_format(data_file_path)
            file_size_mb = FileHandler.get_file_size_mb(data_file_path)
            
            # 加载元数据以确定业务类型
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
            
            business_type_id = metadata.get('business_type_id')
            logger.info(f"文件格式: {file_format}, 大小: {file_size_mb:.2f}MB, 业务类型: {business_type_id}")
            
            cleaner_class = CleaningOrchestrator.CLEANERS.get(business_type_id)
            if not cleaner_class:
                return CleaningOrchestrator._build_error_response(
                    f"不支持的业务类型：{business_type_id}",
                    task_id
                )
            cleaner = cleaner_class()
            
            # 提取字段映射：优先从代码中定义的 HEADER_MAPPING 获取，不再依赖元数据文件
            field_mapping = getattr(cleaner_class, 'HEADER_MAPPING', {})
            if not field_mapping:
                # 兼容旧逻辑，如果代码中没定义，尝试从元数据获取
                field_mapping = metadata.get('storage_config', {}).get('database_config', {}).get('field_mapping', {})
            
            if field_mapping:
                logger.info(f"应用字段映射规则，包含 {len(field_mapping)} 个字段映射")
            
            # 判断是否需要分批处理 (Excel数据或大文件)
            # 根据用户要求：Excel大量数据需要逐步清洗入库，JSON可以直接获取
            is_large_excel = (file_format in {'.xlsx', '.xls'} and file_size_mb > 1.0) # 超过1MB的Excel视为大量数据
            is_large_other = (file_size_mb > 50.0) # 其他格式超过50MB开启分批
            
            should_batch = is_large_excel or is_large_other
            
            cleaning_stats = {
                'original_count': 0,
                'cleaned_count': 0,
                'records': [],
                'total_quality_score': 0.0,
                'batch_count': 0
            }
            storage_stats = {
                'inserted_count': 0,
                'failed_count': 0,
                'table_name': BusinessTypeRegistry.get_table_name(business_type_id)
            }
            
            db_manager = DatabaseManager()
            
            # --- 优化点：查重与溯源准备 ---
            # 1. 计算指纹
            file_hash = ""
            if not data_file_path.startswith('oss://'):
                file_hash = FileHandler.get_file_hash(data_file_path)
            
            # 2. 检查是否处理过
            check_sql = "SELECT id FROM processed_files WHERE (file_path = :path OR (file_hash = :hash AND file_hash != '')) AND status IN ('success', 'processing') LIMIT 1"
            if db_manager.execute_sql(check_sql, {'path': data_file_path, 'hash': file_hash}):
                logger.warning(f"文件已处理过或正在处理中，跳过：{data_file_path}")
                return CleaningOrchestrator._build_error_response(f"文件已处理过或正在处理中：{data_file_path}", task_id)

            # 3. 记录初始处理状态
            insert_processed_sql = "INSERT INTO processed_files (file_path, file_hash, business_type, status) VALUES (:path, :hash, :type, 'processing')"
            db_manager.execute_sql(insert_processed_sql, {'path': data_file_path, 'hash': file_hash, 'type': business_type_id})
            
            if should_batch:
                logger.info("启用分批清洗模式...")
                chunk_size = 1000 # 每次处理1000条
                
                # 获取对应的加载器迭代器
                if file_format in {'.xlsx', '.xls'}:
                    records_it = load_excel_file(data_file_path, chunk_size=chunk_size)
                elif file_format == '.csv':
                    records_it = load_csv_file(data_file_path, chunk_lines=chunk_size)
                elif file_format in {'.json', '.jsonl'}:
                    records_it = load_json_file(data_file_path, chunk_lines=chunk_size)
                else:
                    records_it = None
                
                if not records_it:
                    return CleaningOrchestrator._build_error_response(f"无法创建分批读取器：{data_file_path}", task_id)
                
                for chunk_idx, chunk in enumerate(records_it):
                    logger.info(f"正在处理第 {chunk_idx + 1} 批次 ({len(chunk)} 条)...")
                    
                    # 1. 应用字段映射
                    mapped_chunk = CleaningOrchestrator._apply_field_mapping(chunk, field_mapping, data_file_path)
                    
                    # 2. 清洗当前批次
                    chunk_result = cleaner.clean(mapped_chunk, enable_llm=enable_llm)
                    
                    # 统计更新
                    cleaning_stats['original_count'] += chunk_result['original_count']
                    cleaning_stats['cleaned_count'] += chunk_result['cleaned_count']
                    cleaning_stats['batch_count'] += 1
                    
                    # 估算质量分 (取平均)
                    batch_quality = CleaningOrchestrator._calculate_quality_score(chunk_result)
                    cleaning_stats['total_quality_score'] += batch_quality
                    
                    # 立即入库
                    if storage_stats['table_name']:
                        s_count, f_count = db_manager.insert_records(
                            storage_stats['table_name'],
                            chunk_result['records']
                        )
                        storage_stats['inserted_count'] += s_count
                        storage_stats['failed_count'] += f_count
                    
                cleaning_result = {
                    'success': True,
                    'original_count': cleaning_stats['original_count'],
                    'cleaned_count': cleaning_stats['cleaned_count'],
                    'records': [], # 分批模式下不返回全量数据
                    'statistics': {
                        'is_batched': True,
                        'avg_quality_score': cleaning_stats['total_quality_score'] / cleaning_stats['batch_count'] if cleaning_stats['batch_count'] > 0 else 0
                    }
                }
            else:
                # 常规模式：一次性处理
                logger.info("执行常规清洗模式...")
                if file_format == '.json' or file_format == '.jsonl':
                    records = load_json_file(data_file_path)
                elif file_format == '.csv':
                    records = load_csv_file(data_file_path)
                elif file_format in {'.xlsx', '.xls'}:
                    records = load_excel_file(data_file_path)
                else:
                    records = None
                
                if not records:
                    return CleaningOrchestrator._build_error_response(f"无法读取数据文件：{data_file_path}", task_id)
                
                # 1. 应用字段映射
                mapped_records = CleaningOrchestrator._apply_field_mapping(records, field_mapping, data_file_path)
                
                # 2. 清洗
                cleaning_result = cleaner.clean(mapped_records, enable_llm=enable_llm)
                if not cleaning_result.get('success'):
                    return CleaningOrchestrator._build_error_response(f"清洗失败：{cleaning_result.get('error')}", task_id)
                
                # 入库
                if storage_stats['table_name']:
                    s_count, f_count = db_manager.insert_records(
                        storage_stats['table_name'],
                        cleaning_result['records']
                    )
                    storage_stats['inserted_count'] = s_count
                    storage_stats['failed_count'] = f_count
            
            # 第5步：生成响应
            logger.info("生成响应...")
            
            # --- 优化点：更新处理状态并清理OSS ---
            db_manager.execute_sql(
                "UPDATE processed_files SET status = 'success', row_count = :count WHERE file_path = :path OR (file_hash = :hash AND file_hash != '')",
                {'path': data_file_path, 'hash': file_hash, 'count': storage_stats['inserted_count']}
            )

            # 如果是OSS文件且处理成功，删除云端文件
            if data_file_path.startswith(('oss://', '/aliyun/')):
                try:
                    from src.file_service.aliyun_client import AliyunOSSClient
                    oss_client = AliyunOSSClient()
                    
                    # 1. 删除数据文件
                    oss_data_path = data_file_path.split('/', 3)[-1] if data_file_path.startswith('oss://') else data_file_path.replace('/aliyun/', '')
                    oss_client.delete_file(oss_data_path)
                    
                    # 2. 删除配套元数据文件
                    if metadata_path:
                        oss_meta_path = metadata_path.split('/', 3)[-1] if metadata_path.startswith('oss://') else metadata_path.replace('/aliyun/', '')
                        oss_client.delete_file(oss_meta_path)
                        
                    logger.info(f"已清理OSS原始文件：{data_file_path}")
                except Exception as e:
                    logger.warning(f"清理OSS原始文件失败：{e}")

            storage_info = {
                'success': storage_stats['failed_count'] == 0,
                'table_name': storage_stats['table_name'],
                'inserted_count': storage_stats['inserted_count'],
                'failed_count': storage_stats['failed_count'],
                'database': 'production'
            }
            
            response = CleaningOrchestrator._build_success_response(
                task_id,
                business_type_id,
                cleaning_result,
                storage_info,
                metadata
            )
            
            logger.info(f"清洗流程完成：task_id={task_id}")
            return response
            
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
    def _apply_field_mapping(records: List[Dict[str, Any]], mapping: Dict[str, str], source_file: str = "") -> List[Dict[str, Any]]:
        """
        应用字段映射，将原始表头转换为标准字段名
        同时注入溯源字段
        """
        if not mapping and not source_file:
            return records
            
        mapped_records = []
        for record in records:
            new_record = {}
            if source_file:
                new_record['source_file'] = source_file # 注入溯源信息
                
            for key, value in record.items():
                # 如果存在映射关系，使用映射后的键名；否则保持原样
                standard_key = mapping.get(key, key)
                new_record[standard_key] = value
            mapped_records.append(new_record)
            
        return mapped_records

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
