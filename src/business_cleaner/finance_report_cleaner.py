# -*- coding: utf-8 -*-
"""财务报表数据清洗器 - 业务类型_6"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class FinanceReportCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗财务报表，记录数：{len(records)}")
        cleaned_records = [
            {
                'report_id': r.get('report_id', ''),
                'company_id': r.get('company_id', ''),
                'report_date': r.get('report_date'),
                'revenue': float(r.get('revenue', 0)) if r.get('revenue') else None,
                'profit': float(r.get('profit', 0)) if r.get('profit') else None,
                'report_type': r.get('report_type', '')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'FINANCE_REPORT',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'report_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
