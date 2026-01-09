# -*- coding: utf-8 -*-
"""企业工商信息数据清洗器 - 业务类型_7"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class EnterpriseInfoCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗企业信息，记录数：{len(records)}")
        cleaned_records = [
            {
                'company_id': r.get('company_id', ''),
                'company_name': StringUtils.clean_text(r.get('company_name', '')),
                'registration_number': r.get('registration_number', ''),
                'founded_date': r.get('founded_date'),
                'industry': r.get('industry', ''),
                'employee_count': r.get('employee_count'),
                'status': r.get('status', '')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'ENTERPRISE_INFO',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'company_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
