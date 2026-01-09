# -*- coding: utf-8 -*-
"""采购订单数据清洗器 - 业务类型_13"""
from typing import List, Dict, Any
from src.utils.logger import get_logger
from src.utils.statistics import Statistics
logger = get_logger(__name__)

class PurchaseOrderCleaner:
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        logger.info(f"清洗采购订单，记录数：{len(records)}")
        cleaned_records = [
            {
                'order_id': r.get('order_id', ''),
                'supplier_id': r.get('supplier_id', ''),
                'purchase_date': r.get('purchase_date'),
                'amount': float(r.get('amount', 0)) if r.get('amount') else None,
                'quantity': int(r.get('quantity', 0)) if r.get('quantity') else None,
                'status': r.get('status', ''),
                'delivery_date': r.get('delivery_date')
            }
            for r in records
        ]
        return {
            'success': True,
            'business_type_id': 'PURCHASE_ORDER',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'order_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': []
            }
        }
