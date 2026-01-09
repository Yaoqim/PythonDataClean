import pandas as pd
from typing import Dict, List, Any

class BaseCleaner:
    """数据清洗基类"""
    
    def __init__(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        self.business_type_id = metadata.get("business_type_id")
        
    def clean(self, data: pd.DataFrame) -> pd.DataFrame:
        """执行清洗流程"""
        # 5个核心步骤
        data = self.deduplicate(data)
        data = self.normalize_fields(data)
        data = self.handle_missing_values(data)
        data = self.handle_abnormal_values(data)
        data = self.quality_check(data)
        return data
    
    def deduplicate(self, data: pd.DataFrame) -> pd.DataFrame:
        """去重处理"""
        return data.drop_duplicates()
    
    def normalize_fields(self, data: pd.DataFrame) -> pd.DataFrame:
        """字段标准化"""
        return data
    
    def handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """缺失值处理"""
        return data
    
    def handle_abnormal_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """异常值处理"""
        return data
    
    def quality_check(self, data: pd.DataFrame) -> pd.DataFrame:
        """质量检查"""
        return data
