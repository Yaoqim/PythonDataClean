# -*- coding: utf-8 -*-
"""房产信息数据清洗器 - 业务类型_11"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class PropertyInfoCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗房产信息，记录数：{len(records)}")
        cleaned_records = [
            {
                'property_id': r.get('property_id', ''),
                'property_name': StringUtils.clean_text(r.get('property_name', '')),
                'location': r.get('location', ''),
                'price': float(r.get('price', 0)) if r.get('price') else None,
                'area': float(r.get('area', 0)) if r.get('area') else None,
                'rooms': int(r.get('rooms', 0)) if r.get('rooms') else None,
                'property_type': r.get('property_type', ''),
                'list_date': r.get('list_date')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'PROPERTY_INFO',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'property_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
