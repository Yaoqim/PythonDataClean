# -*- coding: utf-8 -*-
"""
电商评论数据清洗器

业务类型_2：EC_COMMENT
清洗规则：评论去重、文本清洁、情感分析、时间标准化
"""

from typing import List, Dict, Any, Optional
import re

from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.validation import Validator
from src.utils.statistics import Statistics
from src.ai_service.api_client import get_llm_client

logger = get_logger(__name__)


class ECCommentCleaner:
    """
    电商评论清洗器
    
    清洗目标：
    1. 评论内容去重、去emoji、去spam
    2. 评分有效性检查
    3. 时间标准化
    4. 可选的情感分析
    """
    
    # 表头映射
    HEADER_MAPPING = {
        '评论ID': 'comment_id',
        'comment_id': 'comment_id',
        '商品ID': 'product_id',
        'product_id': 'product_id',
        '用户ID': 'user_id',
        'user_id': 'user_id',
        '内容': 'content',
        'content': 'content',
        '评分': 'rating',
        'rating': 'rating',
        '时间': 'create_time',
        'create_time': 'create_time',
        '有用数': 'helpful_count',
        'helpful_count': 'helpful_count'
    }
    
    MAX_COMMENT_LEN = 1000
    
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        """
        清洗电商评论数据
        
        Args:
            records: 原始记录列表
            enable_llm: 是否启用LLM进行情感分析
        
        Returns:
            清洗结果字典
        """
        logger.info(f"开始清洗电商评论数据，记录数：{len(records)}")
        
        cleaned_records = []
        errors = []
        
        llm_client = get_llm_client() if enable_llm else None
        
        for idx, record in enumerate(records):
            try:
                cleaned_record = ECCommentCleaner._clean_record(record, llm_client)
                if cleaned_record:
                    cleaned_records.append(cleaned_record)
            except Exception as e:
                errors.append(f"第{idx+1}行清洗失败：{e}")
                logger.warning(f"记录清洗失败：{e}")
        
        # 计算统计信息
        dedup_rate = Statistics.calculate_dedup_rate(cleaned_records, 'comment_id')
        missing_rate = Statistics.calculate_missing_rate(cleaned_records)
        
        logger.info(f"电商评论清洗完成：{len(cleaned_records)}/{len(records)}，去重率：{dedup_rate:.2%}")
        
        return {
            'success': True,
            'business_type_id': 'EC_COMMENT',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': dedup_rate,
                'missing_rate': missing_rate,
                'errors': errors
            }
        }
    
    @staticmethod
    def _clean_record(record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条评论记录
        
        Args:
            record: 原始记录
            llm_client: LLM客户端
        
        Returns:
            清洗后的记录
        """
        cleaned = {}
        
        # 评论ID（必填）
        comment_id = record.get('comment_id', '').strip()
        if not comment_id:
            logger.warning("缺少comment_id，跳过记录")
            return None
        cleaned['comment_id'] = comment_id
        
        # 商品ID
        product_id = record.get('product_id', '').strip()
        cleaned['product_id'] = product_id
        
        # 用户ID
        user_id = record.get('user_id', '').strip()
        cleaned['user_id'] = user_id
        
        # 评论内容
        content = record.get('content', '').strip()
        if content:
            # 去除emoji、HTML、链接等
            content = StringUtils.remove_emoji(content)
            content = StringUtils.remove_html_tags(content)
            content = StringUtils.remove_urls(content)
            content = StringUtils.remove_special_chars(content)
            content = StringUtils.truncate_text(content, ECCommentCleaner.MAX_COMMENT_LEN)
        cleaned['content'] = content
        
        # 评分
        rating_str = record.get('rating', '')
        rating = ECCommentCleaner._parse_rating(rating_str)
        cleaned['rating'] = rating
        
        # 创建时间
        create_time = record.get('create_time')
        if create_time:
            create_time = TimeUtils.standardize_timestamp(create_time)
        cleaned['create_time'] = create_time
        
        # 有用数
        helpful_count_str = record.get('helpful_count', '')
        helpful_count = ECCommentCleaner._parse_count(helpful_count_str)
        cleaned['helpful_count'] = helpful_count
        
        # 可选的LLM情感分析
        if llm_client and content:
            sentiment_result = llm_client.sentiment_analysis(content)
            if sentiment_result:
                cleaned['sentiment'] = sentiment_result.get('sentiment')
                cleaned['sentiment_confidence'] = sentiment_result.get('confidence')
        
        return cleaned
    
    @staticmethod
    def _parse_rating(rating_str: Any) -> Optional[int]:
        """
        解析评分（1-5分）
        
        支持格式：
        - "5"
        - "5星"
        - "5/5"
        """
        if not rating_str:
            return None
        
        rating_str = str(rating_str).strip()
        
        # 提取数字
        numbers = re.findall(r'\d+', rating_str)
        
        if numbers:
            try:
                rating = int(numbers[0])
                if 1 <= rating <= 5:
                    return rating
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def _parse_count(count_str: Any) -> Optional[int]:
        """
        解析计数（有用数、回复数等）
        
        支持格式：
        - "123"
        - "1k"
        - "1w"
        """
        if not count_str:
            return None
        
        count_str = str(count_str).strip().lower()
        
        try:
            if count_str.endswith('k'):
                return int(float(count_str[:-1]) * 1000)
            elif count_str.endswith('w'):
                return int(float(count_str[:-1]) * 10000)
            else:
                return int(count_str)
        except ValueError:
            logger.debug(f"计数解析失败：{count_str}")
            return None
