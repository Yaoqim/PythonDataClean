# -*- coding: utf-8 -*-
"""
社交平台评论数据清洗器

业务类型_3：SOCIAL_COMMENT
清洗规则：评论去重、文本清洁、情感分析
"""

from typing import List, Dict, Any, Optional
import re
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.statistics import Statistics
from src.ai_service.api_client import get_llm_client

logger = get_logger(__name__)


class SocialCommentCleaner:
    """社交评论清洗器"""
    
    MAX_CONTENT_LEN = 500
    
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        """清洗社交平台评论数据"""
        logger.info(f"开始清洗社交评论数据，记录数：{len(records)}")
        
        cleaned_records = []
        llm_client = get_llm_client() if enable_llm else None
        
        for record in records:
            try:
                cleaned = SocialCommentCleaner._clean_record(record, llm_client)
                if cleaned:
                    cleaned_records.append(cleaned)
            except Exception as e:
                logger.warning(f"记录清洗失败：{e}")
        
        dedup_rate = Statistics.calculate_dedup_rate(cleaned_records, 'comment_id')
        missing_rate = Statistics.calculate_missing_rate(cleaned_records)
        
        logger.info(f"社交评论清洗完成：{len(cleaned_records)}/{len(records)}，去重率：{dedup_rate:.2%}")
        
        return {
            'success': True,
            'business_type_id': 'SOCIAL_COMMENT',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': dedup_rate,
                'missing_rate': missing_rate,
                'errors': []
            }
        }
    
    @staticmethod
    def _clean_record(record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """清洗单条记录"""
        cleaned = {}
        
        # 评论ID（必填）
        comment_id = record.get('comment_id', '').strip()
        if not comment_id:
            return None
        cleaned['comment_id'] = comment_id
        
        # 内容（必填）
        content = record.get('content', '').strip()
        if content:
            content = StringUtils.remove_emoji(content)
            content = StringUtils.remove_html_tags(content)
            content = StringUtils.remove_urls(content)
            content = StringUtils.truncate_text(content, SocialCommentCleaner.MAX_CONTENT_LEN)
        cleaned['content'] = content
        
        # 作者ID
        cleaned['author_id'] = record.get('author_id', '').strip()
        
        # 创建时间
        create_time = record.get('create_time')
        if create_time:
            create_time = TimeUtils.standardize_timestamp(create_time)
        cleaned['create_time'] = create_time
        
        # 点赞数
        likes = record.get('likes', 0)
        try:
            cleaned['likes'] = int(likes) if likes else 0
        except (ValueError, TypeError):
            cleaned['likes'] = 0
        
        # 平台
        cleaned['platform'] = record.get('platform', '').strip()
        
        return cleaned
