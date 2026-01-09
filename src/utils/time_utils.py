# -*- coding: utf-8 -*-
"""
时间处理模块

提供时间标准化、转换、验证等功能。
支持相对时间转绝对时间、时间戳统一等。
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Tuple
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 标准时间格式
STANDARD_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
STANDARD_DATE_FORMAT = "%Y-%m-%d"


class TimeUtils:
    """
    时间处理工具类
    
    提供时间标准化、转换、验证等功能
    """
    
    # 相对时间正则表达式
    RELATIVE_TIME_PATTERNS = {
        r"(\d+)\s*年前": ("years", -1),
        r"(\d+)\s*个月前": ("months", -1),
        r"(\d+)\s*周前": ("weeks", -1),
        r"(\d+)\s*天前": ("days", -1),
        r"(\d+)\s*小时前": ("hours", -1),
        r"(\d+)\s*分钟前": ("minutes", -1),
        r"(\d+)\s*秒前": ("seconds", -1),
        r"刚刚|刚才": ("minutes", -5),
        r"今天|今日": ("days", 0),
        r"昨天|昨日": ("days", -1),
        r"前天": ("days", -2),
        r"明天|明日": ("days", 1),
    }
    
    @staticmethod
    def standardize_timestamp(
        timestamp_str: str,
        target_format: str = STANDARD_TIME_FORMAT
    ) -> Optional[str]:
        """
        将各种格式的时间戳转为标准格式
        
        Args:
            timestamp_str: 时间戳字符串
            target_format: 目标格式（默认为YYYY-MM-DD HH:MM:SS）
        
        Returns:
            标准格式的时间字符串，或None（如果转换失败）
        """
        if not timestamp_str:
            return None
        
        timestamp_str = timestamp_str.strip()
        
        # 常见时间格式列表
        common_formats = [
            STANDARD_TIME_FORMAT,
            STANDARD_DATE_FORMAT,
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y-%m-%d %H:%M",
            "%Y年%m月%d日 %H:%M:%S",
            "%Y年%m月%d日",
            "%Y.%m.%d %H:%M:%S",
            "%Y.%m.%d",
            "%d-%m-%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y%m%d%H%M%S",
            "%Y%m%d",
        ]
        
        # 尝试各种格式
        for fmt in common_formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.strftime(target_format)
            except ValueError:
                continue
        
        # 尝试解析为时间戳（秒）
        try:
            timestamp = float(timestamp_str)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime(target_format)
        except (ValueError, OSError):
            pass
        
        logger.warning(f"无法解析时间戳：{timestamp_str}")
        return None
    
    @staticmethod
    def convert_relative_to_absolute(
        relative_time: str,
        base_time: Optional[datetime] = None
    ) -> Optional[datetime]:
        """
        将相对时间转为绝对时间
        
        Args:
            relative_time: 相对时间字符串（如"3天前"、"刚刚"）
            base_time: 基础时间（默认为当前时间）
        
        Returns:
            datetime对象，或None（如果无法解析）
        
        示例：
            dt = convert_relative_to_absolute("3天前")
            print(dt)  # 3天前的具体日期时间
        """
        if not relative_time:
            return None
        
        relative_time = relative_time.strip()
        base_time = base_time or datetime.now()
        
        # 遍历所有正则表达式
        for pattern, (unit, multiplier) in TimeUtils.RELATIVE_TIME_PATTERNS.items():
            match = re.search(pattern, relative_time)
            if match:
                # 提取数字（如果有）
                if match.groups() and match.groups()[0]:
                    value = int(match.groups()[0]) * multiplier
                else:
                    value = multiplier
                
                # 根据单位计算时间差
                try:
                    if unit == "years":
                        result = base_time + timedelta(days=value * 365)
                    elif unit == "months":
                        result = base_time + timedelta(days=value * 30)
                    elif unit == "weeks":
                        result = base_time + timedelta(weeks=value)
                    elif unit == "days":
                        result = base_time + timedelta(days=value)
                    elif unit == "hours":
                        result = base_time + timedelta(hours=value)
                    elif unit == "minutes":
                        result = base_time + timedelta(minutes=value)
                    elif unit == "seconds":
                        result = base_time + timedelta(seconds=value)
                    else:
                        continue
                    
                    return result
                    
                except Exception as e:
                    logger.warning(f"相对时间转换失败：{relative_time}，错误：{e}")
                    continue
        
        logger.warning(f"无法识别相对时间格式：{relative_time}")
        return None
    
    @staticmethod
    def validate_time_range(
        timestamp: datetime,
        min_time: Optional[datetime] = None,
        max_time: Optional[datetime] = None
    ) -> bool:
        """
        验证时间是否在指定范围内
        
        Args:
            timestamp: 要验证的时间
            min_time: 最小时间
            max_time: 最大时间
        
        Returns:
            True表示在范围内，False表示超出范围
        """
        if min_time and timestamp < min_time:
            logger.warning(f"时间早于最小值：{timestamp} < {min_time}")
            return False
        
        if max_time and timestamp > max_time:
            logger.warning(f"时间晚于最大值：{timestamp} > {max_time}")
            return False
        
        return True
    
    @staticmethod
    def calculate_time_diff(
        start_time: datetime,
        end_time: datetime,
        unit: str = "minutes"
    ) -> float:
        """
        计算两个时间之间的差值
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            unit: 单位（seconds/minutes/hours/days）
        
        Returns:
            时间差（指定单位）
        """
        diff = end_time - start_time
        
        if unit == "seconds":
            return diff.total_seconds()
        elif unit == "minutes":
            return diff.total_seconds() / 60
        elif unit == "hours":
            return diff.total_seconds() / 3600
        elif unit == "days":
            return diff.days
        else:
            raise ValueError(f"不支持的单位：{unit}")


# 便利函数
def standardize_timestamp(
    timestamp_str: str,
    target_format: str = STANDARD_TIME_FORMAT
) -> Optional[str]:
    """
    快速时间标准化
    """
    return TimeUtils.standardize_timestamp(timestamp_str, target_format)


def convert_relative_to_absolute(
    relative_time: str,
    base_time: Optional[datetime] = None
) -> Optional[datetime]:
    """
    快速相对时间转绝对时间
    """
    return TimeUtils.convert_relative_to_absolute(relative_time, base_time)
