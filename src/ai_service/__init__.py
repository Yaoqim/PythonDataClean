# -*- coding: utf-8 -*-
"""
AI服务模块

负责与大语言模型（LLM）的集成，用于高级数据清洗（如情感分析、主题分类等）。

本实现支持可选的LLM集成，如不配置则跳过高级处理。

模块功能：
1. api_client.py - LLM API客户端
"""

from src.ai_service.api_client import AIClient, analyze_text, classify_content

__all__ = [
    "AIClient",
    "analyze_text",
    "classify_content",
]
