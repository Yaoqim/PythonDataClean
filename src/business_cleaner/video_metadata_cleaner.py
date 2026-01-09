# -*- coding: utf-8 -*-
"""短视频元数据清洗器 - 业务类型_9"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class VideoMetadataCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗短视频元数据，记录数：{len(records)}")
        cleaned_records = [
            {
                'video_id': r.get('video_id', ''),
                'title': StringUtils.clean_text(r.get('title', '')),
                'description': StringUtils.clean_text(r.get('description', '')),
                'author_id': r.get('author_id', ''),
                'duration': int(r.get('duration', 0)) if r.get('duration') else None,
                'upload_time': r.get('upload_time'),
                'views': r.get('views', 0),
                'likes': r.get('likes', 0),
                'tags': r.get('tags', [])
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'VIDEO_METADATA',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'video_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
