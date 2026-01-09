# -*- coding: utf-8 -*-
"""
大模型API客户端

支持主流LLM服务：
- OpenAI GPT系列
- Anthropic Claude
- 阿里云通义千问
- 其他本地/云端模型
"""

from typing import Dict, Any, Optional, List
import requests
import json

from src.utils.logger import get_logger
from config.settings import Settings

logger = get_logger(__name__)


class LLMClient:
    """
    大模型客户端
    
    负责：
    1. 调用LLM API进行复杂语义分析
    2. 情感分析
    3. 主题分类
    4. 文本改写等高级清洗
    """
    
    def __init__(self):
        """初始化LLM客户端"""
        self.api_key = Settings.LLM_API_KEY
        self.api_base = Settings.LLM_API_BASE
        self.model = Settings.LLM_MODEL
        self.temperature = Settings.LLM_TEMPERATURE
        self.max_tokens = Settings.LLM_MAX_TOKENS
    
    def call_llm(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        调用LLM
        
        Args:
            prompt: 提示词
            context: 上下文信息
        
        Returns:
            LLM响应文本
        """
        if not self.api_key:
            logger.warning("LLM API密钥未配置，跳过LLM调用")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': '你是数据清洗助手，帮助进行数据分析和清洗'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }
            
            response = requests.post(
                f'{self.api_base}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"LLM调用失败：{response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"LLM调用异常：{e}")
            return None
    
    def sentiment_analysis(self, text: str) -> Optional[Dict[str, Any]]:
        """
        情感分析
        
        Args:
            text: 文本内容
        
        Returns:
            情感分析结果
        """
        prompt = f"""
        分析以下文本的情感倾向，返回JSON格式结果：
        {text}
        
        返回格式：
        {{
            "sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "keywords": []
        }}
        """
        
        response = self.call_llm(prompt)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"情感分析结果解析失败：{response}")
                return None
        
        return None
    
    def topic_classification(self, text: str, categories: List[str]) -> Optional[Dict[str, Any]]:
        """
        主题分类
        
        Args:
            text: 文本内容
            categories: 分类范围
        
        Returns:
            分类结果
        """
        categories_str = ', '.join(categories)
        prompt = f"""
        将以下文本分类到一个最合适的类别，返回JSON格式结果：
        
        文本：{text}
        
        可选类别：{categories_str}
        
        返回格式：
        {{
            "category": "类别名称",
            "confidence": 0.0-1.0,
            "reason": "分类原因"
        }}
        """
        
        response = self.call_llm(prompt)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"分类结果解析失败：{response}")
                return None
        
        return None
    
    def entity_extraction(self, text: str) -> Optional[Dict[str, Any]]:
        """
        实体提取
        
        Args:
            text: 文本内容
        
        Returns:
            提取的实体列表
        """
        prompt = f"""
        从以下文本中提取关键实体，返回JSON格式结果：
        {text}
        
        返回格式：
        {{
            "entities": [
                {{"type": "实体类型", "value": "实体值"}},
                ...
            ]
        }}
        """
        
        response = self.call_llm(prompt)
        
        if response:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning(f"实体提取结果解析失败：{response}")
                return None
        
        return None


def get_llm_client() -> LLMClient:
    """获取LLM客户端单例"""
    return LLMClient()
