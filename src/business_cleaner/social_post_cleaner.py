# -*- coding: utf-8 -*-
"""社交平台帖子数据清洗器 - 业务类型_4"""
from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class SocialPostCleaner:
    MAX_CONTENT_LEN = 1000
    
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗社交帖子，记录数：{len(records)}")
        cleaned_records = []
        for record in records:
            cleaned = SocialPostCleaner._clean_record(record)
            if cleaned:
                cleaned_records.append(cleaned)
        return {
            'success': True,
            'business_type_id': 'SOCIAL_POST',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'post_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
    
    @staticmethod
    def _clean_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        post_id = record.get('post_id', '').strip()
        if not post_id:
            return None
        cleaned = {
            'post_id': post_id,
            'content': StringUtils.clean_text(record.get('content', '')),
            'author_id': record.get('author_id', '').strip(),
            'create_time': TimeUtils.standardize_timestamp(record.get('create_time')) if record.get('create_time') else None,
            'likes': int(record.get('likes', 0)) if record.get('likes') else 0,
            'shares': int(record.get('shares', 0)) if record.get('shares') else 0,
            'comments_count': int(record.get('comments_count', 0)) if record.get('comments_count') else 0
        }
        return cleaned
