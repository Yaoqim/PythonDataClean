# -*- coding: utf-8 -*-
"""招聘岗位数据清洗器 - 业务类型_8"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class RecruitJobCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗招聘岗位，记录数：{len(records)}")
        cleaned_records = [
            {
                'job_id': r.get('job_id', ''),
                'job_title': StringUtils.clean_text(r.get('job_title', '')),
                'company_id': r.get('company_id', ''),
                'salary_min': float(r.get('salary_min', 0)) if r.get('salary_min') else None,
                'salary_max': float(r.get('salary_max', 0)) if r.get('salary_max') else None,
                'location': r.get('location', ''),
                'job_type': r.get('job_type', ''),
                'publish_date': r.get('publish_date')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'RECRUIT_JOB',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'job_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
