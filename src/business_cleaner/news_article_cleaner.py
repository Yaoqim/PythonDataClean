# -*- coding: utf-8 -*-
"""资讯文章数据清洗器 - 业务类型_5"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class NewsArticleCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗资讯文章，记录数：{len(records)}")
        cleaned_records = [
            {
                'article_id': r.get('article_id', ''),
                'title': StringUtils.clean_text(r.get('title', '')),
                'content': StringUtils.clean_text(r.get('content', '')),
                'source': r.get('source', ''),
                'publish_time': r.get('publish_time'),
                'category': r.get('category', ''),
                'views': r.get('views', 0)
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'NEWS_ARTICLE',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'article_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
