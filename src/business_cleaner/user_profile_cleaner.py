# -*- coding: utf-8 -*-
"""用户基础信息清洗器 - 业务类型_10"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class UserProfileCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗用户信息，记录数：{len(records)}")
        cleaned_records = [
            {
                'user_id': r.get('user_id', ''),
                'username': StringUtils.clean_text(r.get('username', '')),
                'email': r.get('email', '').lower().strip(),
                'phone': r.get('phone', ''),
                'age': int(r.get('age', 0)) if r.get('age') else None,
                'gender': r.get('gender', ''),
                'city': r.get('city', ''),
                'registration_date': r.get('registration_date')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'USER_PROFILE',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'user_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
