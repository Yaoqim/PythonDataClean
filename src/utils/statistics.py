# -*- coding: utf-8 -*-
"""
统计工具模块

提供数据清洗统计功能：
- 去重率计算
- 缺失率计算
- 质量报告生成
"""

from typing import List, Dict, Any, Optional
from collections import Counter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Statistics:
    """
    统计工具类
    
    提供数据清洗过程中的各类统计功能
    """
    
    @staticmethod
    def calculate_dedup_rate(
        records: List[Dict[str, Any]],
        key_field: str
    ) -> float:
        """
        计算去重率（基于关键字段）
        
        Args:
            records: 清洗后的记录列表
            key_field: 关键字段名（用于识别重复）
        
        Returns:
            去重率（0-1之间的浮点数）
        """
        if not records:
            return 0.0
        
        # 统计关键字段的唯一值
        unique_ids = set()
        for record in records:
            if key_field in record:
                unique_ids.add(record[key_field])
        
        unique_count = len(unique_ids)
        total_count = len(records)
        
        # 去重率 = (总数 - 唯一值数) / 总数
        if total_count == 0:
            return 0.0
        
        dedup_rate = (total_count - unique_count) / total_count
        return round(dedup_rate, 4)
    
    @staticmethod
    def calculate_missing_rate(
        records: List[Dict[str, Any]],
        field_name: Optional[str] = None
    ) -> float:
        """
        计算字段或整体缺失率
        
        Args:
            records: 记录列表
            field_name: 字段名（如果None会计算整体缺失率）
        
        Returns:
            缺失率（0-1之间的浮点数）
        """
        if not records:
            return 0.0
        
        if field_name:
            # 计算指定字段的缺失率
            missing_count = 0
            for record in records:
                if field_name not in record or record[field_name] is None or record[field_name] == '':
                    missing_count += 1
            
            missing_rate = missing_count / len(records)
            return round(missing_rate, 4)
        else:
            # 计算整体缺失率（所有字段有效值的记录比例）
            all_fields = set()
            for record in records:
                all_fields.update(record.keys())
            
            valid_record_count = 0
            for record in records:
                has_missing = False
                for field in all_fields:
                    if field not in record or record[field] is None or record[field] == '':
                        has_missing = True
                        break
                if not has_missing:
                    valid_record_count += 1
            
            missing_rate = (len(records) - valid_record_count) / len(records)
            return round(missing_rate, 4)
    
    @staticmethod
    def calculate_missing_rates(
        records: List[Dict[str, Any]],
        fields: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        计算多个字段的缺失率
        
        Args:
            records: 记录列表
            fields: 字段名列表（如果为None，计算所有字段）
        
        Returns:
            字段名到缺失率的映射
        """
        if not records:
            return {}
        
        # 确定要计算的字段
        if fields is None:
            fields = set()
            for record in records:
                fields.update(record.keys())
            fields = list(fields)
        
        missing_rates = {}
        for field in fields:
            missing_rate = Statistics.calculate_missing_rate(records, field)
            missing_rates[field] = missing_rate
        
        return missing_rates
    
    @staticmethod
    def get_field_statistics(
        records: List[Dict[str, Any]],
        field_name: str
    ) -> Dict[str, Any]:
        """
        获取字段的统计信息
        
        Args:
            records: 记录列表
            field_name: 字段名
        
        Returns:
            包含统计信息的字典
        """
        values = []
        missing_count = 0
        
        for record in records:
            if field_name in record and record[field_name] is not None:
                values.append(record[field_name])
            else:
                missing_count += 1
        
        stats = {
            "total_count": len(records),
            "valid_count": len(values),
            "missing_count": missing_count,
            "missing_rate": Statistics.calculate_missing_rate(records, field_name),
        }
        
        # 如果值是数值型，计算统计量
        if values and isinstance(values[0], (int, float)):
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                stats["min"] = min(numeric_values)
                stats["max"] = max(numeric_values)
                stats["avg"] = sum(numeric_values) / len(numeric_values)
                stats["sum"] = sum(numeric_values)
        
        # 如果值较少，列出最常见的值
        if values:
            value_counts = Counter(values)
            most_common = value_counts.most_common(5)
            stats["top_values"] = [
                {"value": v, "count": c} for v, c in most_common
            ]
        
        return stats
    
    @staticmethod
    def generate_cleaning_report(
        original_count: int,
        cleaned_count: int,
        field_statistics: Dict[str, Dict[str, Any]],
        cleaning_time_seconds: float,
        errors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成完整的清洗报告
        
        Args:
            original_count: 原始记录数
            cleaned_count: 清洗后有效记录数
            field_statistics: 字段统计信息
            cleaning_time_seconds: 清洗耗时（秒）
            errors: 错误信息列表
        
        Returns:
            完整的清洗报告字典
        """
        report = {
            "summary": {
                "original_count": original_count,
                "cleaned_count": cleaned_count,
                "deleted_count": original_count - cleaned_count,
                "success_rate": (cleaned_count / original_count * 100) if original_count > 0 else 0,
                "cleaning_time_seconds": round(cleaning_time_seconds, 2),
                "records_per_second": round(original_count / cleaning_time_seconds, 2) if cleaning_time_seconds > 0 else 0,
            },
            "field_statistics": field_statistics,
        }
        
        if errors:
            report["errors"] = errors
        
        return report
    
    @staticmethod
    def format_report_text(report: Dict[str, Any]) -> str:
        """
        将报告格式化为可读的文本
        
        Args:
            report: 清洗报告字典
        
        Returns:
            格式化后的文本
        """
        lines = []
        
        summary = report.get("summary", {})
        lines.append("=" * 60)
        lines.append("数据清洗统计报告")
        lines.append("=" * 60)
        lines.append(f"原始记录数: {summary.get('original_count', 0)}")
        lines.append(f"清洗后记录数: {summary.get('cleaned_count', 0)}")
        lines.append(f"删除记录数: {summary.get('deleted_count', 0)}")
        lines.append(f"成功率: {summary.get('success_rate', 0):.2f}%")
        lines.append(f"清洗耗时: {summary.get('cleaning_time_seconds', 0)}秒")
        lines.append(f"处理速度: {summary.get('records_per_second', 0):.2f}条/秒")
        
        # 字段统计
        field_stats = report.get("field_statistics", {})
        if field_stats:
            lines.append("")
            lines.append("字段统计:")
            lines.append("-" * 60)
            for field, stats in field_stats.items():
                lines.append(f"  {field}:")
                lines.append(f"    - 有效值: {stats.get('valid_count', 0)}")
                lines.append(f"    - 缺失值: {stats.get('missing_count', 0)}")
                lines.append(f"    - 缺失率: {stats.get('missing_rate', 0):.2f}%")
        
        # 错误信息
        errors = report.get("errors", [])
        if errors:
            lines.append("")
            lines.append("错误信息:")
            lines.append("-" * 60)
            for error in errors:
                lines.append(f"  - {error}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


# 便利函数
def calculate_dedup_rate(
    original_count: int,
    deduplicated_count: int
) -> float:
    """快速计算去重率"""
    return Statistics.calculate_dedup_rate(original_count, deduplicated_count)


def calculate_missing_rate(
    records: List[Dict[str, Any]],
    field_name: str
) -> float:
    """快速计算缺失率"""
    return Statistics.calculate_missing_rate(records, field_name)


def generate_cleaning_report(
    original_count: int,
    cleaned_count: int,
    field_statistics: Dict[str, Dict[str, Any]],
    cleaning_time_seconds: float,
    errors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """快速生成清洗报告"""
    return Statistics.generate_cleaning_report(
        original_count, cleaned_count, field_statistics, cleaning_time_seconds, errors
    )
