import json
import os
from typing import Dict, Any

class MetadataLoader:
    """元数据加载器"""
    
    @staticmethod
    def load_metadata(metadata_file: str) -> Dict[str, Any]:
        """加载元数据文件"""
        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"元数据文件不存在: {metadata_file}")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return metadata
    
    @staticmethod
    def load_clean_config(business_type_id: str) -> Dict[str, Any]:
        """加载业务类型的清洗配置"""
        config_dir = "config/metadata_rules"
        config_file = os.path.join(config_dir, f"{business_type_id}.json")
        
        if not os.path.exists(config_file):
            config_file = os.path.join(config_dir, "default_rule.json")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
