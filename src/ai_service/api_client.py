# -*- coding: utf-8 -*-
"""
LLM API客户端模块

负责与OpenAI等LLM服务的集成，用于高级文本分析。

功能：
- 情感分析
- 文本分类
- 内容摘要
- 实体识别等

设计：可选集成，如未配置则返回None或默认值
"""

from typing import Optional, Dict, Any, List
import requests
import time

from config.settings import Settings
from src.utils.logger import get_logger
from src.utils.error_handler import ErrorHandler

logger = get_logger(__name__)


class AIClient:
    """
    LLM API客户端
    
    负责：
    1. 与LLM服务通信
    2. 文本分析任务（情感、分类等）
    3. 结果缓存和速率限制
    """
    
    def __init__(self):
        """初始化AI客户端"""
        self.api_key = Settings.LLM_API_KEY
        self.api_base = Settings.LLM_API_BASE
        self.model = Settings.LLM_MODEL
        self.temperature = Settings.LLM_TEMPERATURE
        self.max_tokens = Settings.LLM_MAX_TOKENS
        
        # 检查是否配置了API
        self.enabled = bool(self.api_key and self.api_base)
        
        if not self.enabled:
            logger.warning("LLM API未配置，高级文本分析功能已禁用")
        else:
            logger.info(f"LLM API已启用：{self.api_base}")
    
    def is_enabled(self) -> bool:
        """
        检查AI功能是否启用
        
        Returns:
            True表示启用，False表示禁用
        """
        return self.enabled
    
    def analyze_sentiment(
        self,
        text: str,
        language: str = "zh"
    ) -> Optional[Dict[str, Any]]:
        """
        分析文本情感
        
        Args:
            text: 要分析的文本
            language: 语言（zh/en）
        
        Returns:
            包含情感标签和置信度的字典，如禁用返回None
        
        示例：
            result = client.analyze_sentiment("这个商品很好用！")
            # {"sentiment": "positive", "confidence": 0.95, "scores": {...}}
        """
        if not self.enabled:
            logger.debug("AI功能未启用，跳过情感分析")
            return None
        
        try:
            if not text or len(text.strip()) == 0:
                return None
            
            prompt = f"请分析下面文本的情感。只返回JSON格式：{{'sentiment': 'positive/neutral/negative', 'confidence': 0.0-1.0}}\n文本：{text}"
            
            result = self._call_llm(prompt)
            if result:
                logger.debug(f"情感分析完成：{text[:50]}")
            return result
            
        except Exception as e:
            logger.error(f"情感分析失败：{e}")
            return None
    
    def classify_text(
        self,
        text: str,
        categories: List[str],
        language: str = "zh"
    ) -> Optional[Dict[str, Any]]:
        """
        对文本进行分类
        
        Args:
            text: 要分类的文本
            categories: 分类类别列表
            language: 语言
        
        Returns:
            包含分类结果和置信度的字典，如禁用返回None
        
        示例：
            result = client.classify_text(
                "正品iPhone手机",
                ["电子产品", "服装", "食品"]
            )
            # {"category": "电子产品", "confidence": 0.98}
        """
        if not self.enabled:
            logger.debug("AI功能未启用，跳过文本分类")
            return None
        
        try:
            if not text or len(text.strip()) == 0:
                return None
            
            categories_str = ", ".join(categories)
            prompt = f"请把下面的文本分类到以下类别之一：{categories_str}\n只返回JSON格式：{{'category': '类别', 'confidence': 0.0-1.0}}\n文本：{text}"
            
            result = self._call_llm(prompt)
            if result:
                logger.debug(f"文本分类完成：{text[:50]} -> {result.get('category')}")
            return result
            
        except Exception as e:
            logger.error(f"文本分类失败：{e}")
            return None
    
    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        从文本中提取命名实体
        
        Args:
            text: 要处理的文本
            entity_types: 实体类型（如person/organization/location）
        
        Returns:
            包含实体列表的字典，如禁用返回None
        
        示例：
            result = client.extract_entities(
                "张三在北京的公司工作",
                ["PERSON", "LOCATION", "ORG"]
            )
            # {"entities": [{"text": "张三", "type": "PERSON"}, ...]}
        """
        if not self.enabled:
            logger.debug("AI功能未启用，跳过实体提取")
            return None
        
        try:
            if not text or len(text.strip()) == 0:
                return None
            
            types_str = ", ".join(entity_types) if entity_types else "PERSON, LOCATION, ORGANIZATION"
            prompt = f"请从下面的文本中提取{types_str}类型的实体。返回JSON格式的列表：[{{'text': '实体', 'type': '类型'}}]\n文本：{text}"
            
            result = self._call_llm(prompt)
            if result:
                logger.debug(f"实体提取完成：{text[:50]}")
            return result
            
        except Exception as e:
            logger.error(f"实体提取失败：{e}")
            return None
    
    def _call_llm(self, prompt: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        调用LLM API
        
        Args:
            prompt: 提示文本
            max_retries: 最大重试次数
        
        Returns:
            LLM返回的结果，如调用失败返回None
        """
        if not self.enabled:
            return None
        
        try:
            url = f"{self.api_base}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # 重试逻辑
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        # 尝试解析JSON
                        try:
                            import json
                            return json.loads(content)
                        except:
                            return {"content": content}
                    
                    elif response.status_code == 429:
                        # 速率限制，等待后重试
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"API速率限制，等待{wait_time}秒后重试...")
                        time.sleep(wait_time)
                        continue
                    
                    else:
                        logger.error(f"LLM API错误：{response.status_code} {response.text}")
                        return None
                        
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        logger.warning(f"请求失败，等待{wait_time}秒后重试：{e}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"LLM API请求最终失败：{e}")
                        return None
            
            return None
            
        except Exception as e:
            logger.error(f"调用LLM API异常：{e}")
            return None


# 全局AI客户端实例
_ai_client = None


def get_ai_client() -> AIClient:
    """
    获取全局AI客户端实例
    
    Returns:
        AIClient实例
    """
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


def analyze_text(text: str, analysis_type: str = "sentiment") -> Optional[Dict[str, Any]]:
    """
    便利函数：分析文本
    
    Args:
        text: 要分析的文本
        analysis_type: 分析类型（sentiment/classification等）
    
    Returns:
        分析结果
    
    示例：
        result = analyze_text("很好的商品", analysis_type="sentiment")
    """
    client = get_ai_client()
    
    if analysis_type == "sentiment":
        return client.analyze_sentiment(text)
    else:
        logger.warning(f"未知的分析类型：{analysis_type}")
        return None


def classify_content(
    text: str,
    categories: List[str]
) -> Optional[Dict[str, Any]]:
    """
    便利函数：分类文本
    
    Args:
        text: 要分类的文本
        categories: 类别列表
    
    Returns:
        分类结果
    
    示例：
        result = classify_content("iPhone手机", ["电子产品", "服装"])
    """
    client = get_ai_client()
    return client.classify_text(text, categories)
