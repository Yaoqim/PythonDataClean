# -*- coding: utf-8 -*-
"""
清洗器基类

定义所有业务类型清洗器必须遵循的标准接口。

每个具体的清洗器都应继承此基类并实现_clean_record()方法。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseCleaner(ABC):
    """
    数据清洗器基类
    
    定义清洗流程的标准框架，具体业务类型通过继承此类并实现_clean_record()方法
    """
    
    # 业务类型ID（子类必须重写）
    BUSINESS_TYPE_ID = None
    
    # 主键字段（子类必须重写）
    PRIMARY_KEY = None
    
    # 必需字段列表（子类可重写）
    REQUIRED_FIELDS = []
    
    def __init__(self):
        """初始化清洗器"""
        if not self.BUSINESS_TYPE_ID:
            raise ValueError(f"{self.__class__.__name__}必须定义BUSINESS_TYPE_ID")
        if not self.PRIMARY_KEY:
            raise ValueError(f"{self.__class__.__name__}必须定义PRIMARY_KEY")
        
        logger.info(f"初始化清洗器：{self.BUSINESS_TYPE_ID}")
    
    @abstractmethod
    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条记录
        
        子类必须实现此方法
        
        Args:
            record: 原始记录
            llm_client: LLM客户端（可选，用于高级处理）
        
        Returns:
            清洗后的记录，如无法清洗返回None
        """
        pass
    
    def clean(
        self,
        records: List[Dict[str, Any]],
        llm_client: Any = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        清洗记录集合
        
        执行5步清洗流程：
        1. 明确目标（验证记录）
        2. 去重
        3. 字段标准化
        4. 缺失值处理
        5. 异常值检测
        
        Args:
            records: 原始记录列表
            llm_client: LLM客户端
        
        Returns:
            (清洗后的记录列表, 清洗统计信息)
        """
        if not records:
            return [], {
                'original_count': 0,
                'cleaned_count': 0,
                'success_rate': 0.0
            }
        
        original_count = len(records)
        stats = {
            'business_type': self.BUSINESS_TYPE_ID,
            'original_count': original_count,
        }
        
        # 步骤1：逐条清洗
        cleaned_records = []
        for record in records:
            try:
                cleaned = self._clean_record(record, llm_client)
                if cleaned is not None:
                    cleaned_records.append(cleaned)
            except Exception as e:
                logger.warning(f"记录清洗失败：{e}")
        
        stats['cleaned_count'] = len(cleaned_records)
        stats['failed_count'] = original_count - len(cleaned_records)
        stats['success_rate'] = round(
            len(cleaned_records) / original_count if original_count > 0 else 0,
            4
        )
        
        logger.info(
            f"{self.BUSINESS_TYPE_ID}清洗完成：原始{original_count}条，"
            f"清洗成功{len(cleaned_records)}条，成功率{stats['success_rate']:.2%}"
        )
        
        return cleaned_records, stats
    
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        验证记录的基本有效性
        
        Args:
            record: 记录
        
        Returns:
            True表示有效，False表示无效
        """
        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None or record[field] == '':
                logger.debug(f"必需字段缺失：{field}")
                return False
        
        # 检查主键
        if self.PRIMARY_KEY not in record or not record[self.PRIMARY_KEY]:
            logger.debug(f"主键缺失：{self.PRIMARY_KEY}")
            return False
        
        return True
