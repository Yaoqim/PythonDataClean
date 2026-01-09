# -*- coding: utf-8 -*-
"""
客户对话数据清洗器

业务类型_14：CUSTOMER_DIALOG
清洗规则：对话去重、消息清洁、情感分析、主题分类
"""

from typing import List, Dict, Any, Optional
import json
import re

from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.validation import Validator
from src.utils.statistics import Statistics
from src.ai_service.api_client import get_llm_client

logger = get_logger(__name__)


class CustomerDialogCleaner:
    """
    客户对话清洗器
    
    清洗目标：
    1. 对话去重
    2. 消息清洁、去spam
    3. 情感分析
    4. 主题分类
    """
    
    MAX_MESSAGE_LEN = 500
    DIALOG_TOPICS = ['售前咨询', '订单问题', '退货退款', '物流查询', '产品建议', '投诉建议', '其他']
    
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = True) -> Dict[str, Any]:
        """
        清洗客户对话数据
        
        Args:
            records: 原始记录列表
            enable_llm: 是否启用LLM进行主题分类和情感分析
        
        Returns:
            清洗结果字典
        """
        logger.info(f"开始清洗客户对话数据，记录数：{len(records)}")
        
        cleaned_records = []
        errors = []
        
        llm_client = get_llm_client() if enable_llm else None
        
        for idx, record in enumerate(records):
            try:
                cleaned_record = CustomerDialogCleaner._clean_record(record, llm_client)
                if cleaned_record:
                    cleaned_records.append(cleaned_record)
            except Exception as e:
                errors.append(f"第{idx+1}行清洗失败：{e}")
                logger.warning(f"记录清洗失败：{e}")
        
        # 计算统计信息
        dedup_rate = Statistics.calculate_dedup_rate(cleaned_records, 'dialog_id')
        missing_rate = Statistics.calculate_missing_rate(cleaned_records)
        
        logger.info(f"客户对话清洗完成：{len(cleaned_records)}/{len(records)}，去重率：{dedup_rate:.2%}")
        
        return {
            'success': True,
            'business_type_id': 'CUSTOMER_DIALOG',
            'original_count': len(records),
            'cleaned_count': len(cleaned_records),
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': dedup_rate,
                'missing_rate': missing_rate,
                'errors': errors
            }
        }
    
    @staticmethod
    def _clean_record(record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条对话记录
        
        Args:
            record: 原始记录
            llm_client: LLM客户端
        
        Returns:
            清洗后的记录
        """
        cleaned = {}
        
        # 对话ID（必填）
        dialog_id = record.get('dialog_id', '').strip()
        if not dialog_id:
            logger.warning("缺少dialog_id，跳过记录")
            return None
        cleaned['dialog_id'] = dialog_id
        
        # 客户ID
        customer_id = record.get('customer_id', '').strip()
        cleaned['customer_id'] = customer_id
        
        # 客服ID
        agent_id = record.get('agent_id', '').strip()
        cleaned['agent_id'] = agent_id
        
        # 清洁消息列表
        messages_data = record.get('messages', [])
        cleaned_messages = CustomerDialogCleaner._clean_messages(messages_data)
        cleaned['messages'] = cleaned_messages
        
        # 将清洁后的消息合并成文本用于分析
        message_texts = [msg.get('content', '') for msg in cleaned_messages if msg.get('content')]
        dialog_text = ' '.join(message_texts)
        
        # 初始情感倾向（Python规则）
        sentiment = CustomerDialogCleaner._analyze_sentiment_rule_based(dialog_text)
        cleaned['sentiment'] = sentiment
        
        # 初始主题分类（Python规则）
        topic = CustomerDialogCleaner._classify_topic_rule_based(dialog_text)
        cleaned['topic'] = topic
        
        # LLM优化分类
        if llm_client and dialog_text:
            # 情感分析
            sentiment_result = llm_client.sentiment_analysis(dialog_text)
            if sentiment_result:
                cleaned['sentiment'] = sentiment_result.get('sentiment')
                cleaned['sentiment_confidence'] = sentiment_result.get('confidence')
            
            # 主题分类
            topic_result = llm_client.topic_classification(dialog_text, CustomerDialogCleaner.DIALOG_TOPICS)
            if topic_result:
                cleaned['topic'] = topic_result.get('category')
                cleaned['topic_confidence'] = topic_result.get('confidence')
        
        # 对话时长
        duration = record.get('duration')
        if duration:
            try:
                cleaned['duration'] = int(duration)
            except (ValueError, TypeError):
                cleaned['duration'] = None
        else:
            cleaned['duration'] = None
        
        return cleaned
    
    @staticmethod
    def _clean_messages(messages_data: Any) -> List[Dict[str, Any]]:
        """
        清洁消息列表
        
        Args:
            messages_data: 消息数据（列表或JSON字符串）
        
        Returns:
            清洁后的消息列表
        """
        if not messages_data:
            return []
        
        # 如果是字符串，尝试解析JSON
        if isinstance(messages_data, str):
            try:
                messages_data = json.loads(messages_data)
            except json.JSONDecodeError:
                logger.warning(f"消息JSON解析失败：{messages_data}")
                return []
        
        if not isinstance(messages_data, list):
            return []
        
        cleaned_messages = []
        
        for msg in messages_data:
            if not isinstance(msg, dict):
                continue
            
            cleaned_msg = {}
            
            # 发送者
            sender = msg.get('sender', '').strip()
            cleaned_msg['sender'] = sender
            
            # 消息内容
            content = msg.get('content', '').strip()
            if content:
                content = StringUtils.remove_emoji(content)
                content = StringUtils.remove_html_tags(content)
                content = StringUtils.remove_urls(content)
                content = StringUtils.truncate_text(content, CustomerDialogCleaner.MAX_MESSAGE_LEN)
            cleaned_msg['content'] = content
            
            # 发送时间
            timestamp = msg.get('timestamp')
            if timestamp:
                timestamp = TimeUtils.standardize_timestamp(timestamp)
            cleaned_msg['timestamp'] = timestamp
            
            cleaned_messages.append(cleaned_msg)
        
        return cleaned_messages
    
    @staticmethod
    def _analyze_sentiment_rule_based(dialog_text: str) -> str:
        """
        基于规则的情感分析
        
        Args:
            dialog_text: 对话文本
        
        Returns:
            情感倾向：positive、negative、neutral
        """
        if not dialog_text:
            return 'neutral'
        
        text_lower = dialog_text.lower()
        
        # 负面关键词
        negative_words = ['问题', '错误', '坏', '差', '垃圾', '不满', '投诉', '退货', '赔偿', '失望']
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # 正面关键词
        positive_words = ['好', '满意', '感谢', '谢谢', '完美', '很好', '优秀', '推荐', '五星']
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'
    
    @staticmethod
    def _classify_topic_rule_based(dialog_text: str) -> str:
        """
        基于规则的主题分类
        
        Args:
            dialog_text: 对话文本
        
        Returns:
            主题分类
        """
        text_lower = dialog_text.lower()
        
        # 主题关键词映射
        topic_keywords = {
            '售前咨询': ['咨询', '询问', '了解', '怎么样', '怎么', '哪个', '推荐'],
            '订单问题': ['订单', '下单', '购买', '结账', '支付'],
            '退货退款': ['退货', '退款', '返货', '申请', '处理', '退'],
            '物流查询': ['物流', '快递', '配送', '发货', '追踪', '查询'],
            '产品建议': ['建议', '改进', '功能', '优化', '希望'],
            '投诉建议': ['投诉', '反馈', '问题', '不满'],
            '其他': []
        }
        
        for topic, keywords in topic_keywords.items():
            if topic != '其他':
                for keyword in keywords:
                    if keyword in text_lower:
                        return topic
        
        return '其他'
