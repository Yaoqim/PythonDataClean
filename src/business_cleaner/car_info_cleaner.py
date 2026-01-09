# -*- coding: utf-8 -*-
"""汽车信息数据清洗器 - 业务类型_12"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class CarInfoCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗汽车信息，记录数：{len(records)}")
        cleaned_records = [
            {
                'car_id': r.get('car_id', ''),
                'brand': r.get('brand', ''),
                'model': StringUtils.clean_text(r.get('model', '')),
                'price': float(r.get('price', 0)) if r.get('price') else None,
                'year': int(r.get('year', 0)) if r.get('year') else None,
                'mileage': float(r.get('mileage', 0)) if r.get('mileage') else None,
                'fuel_type': r.get('fuel_type', ''),
                'color': r.get('color', '')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'CAR_INFO',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'car_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
