# -*- coding: utf-8 -*-
"""
客户对话清洗器

业务类型：CUSTOMER_DIALOG
数据表：customer_dialog

清洗规则（参考《业务类型_14客户对话.md》）：

核心字段：
- conversation_id：对话ID（主键、必填）
- customer_id：客户ID（必填）
- service_id：服务人员ID（必填）
- message_content：消息内容（必填）
- message_type：消息类型（必填）
- message_time：消息时间（必填）

清洗流程：
1. 验证主键（conversation_id） - 缺失则删除记录
2. 验证必填字段 - 缺失则删除记录
3. 消息类型验证
4. 文本字段清洁（去emoji、去HTML、保留URL）
5. 时间字段标准化
6. 满意度评分验证（0-5）
7. 可选LLM意图识别
"""

from typing import Dict, Any, Optional
from src.cleaner.base_cleaner import BaseCleaner
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.validation import Validator

logger = get_logger(__name__)


class CustomerDialogCleaner(BaseCleaner):
    """客户对话清洗器"""
    
    # 业务类型标识
    BUSINESS_TYPE_ID = 'CUSTOMER_DIALOG'
    
    # 主键字段
    PRIMARY_KEY = 'conversation_id'
    
    # 必需字段
    REQUIRED_FIELDS = ['conversation_id', 'customer_id', 'service_id', 'message_content', 'message_type', 'message_time']
    
    # 核心字段
    CORE_FIELDS = ['conversation_id', 'customer_id', 'service_id', 'message_content', 'message_type', 'message_time']
    
    # 有效消息类型
    VALID_MESSAGE_TYPES = {'question', 'answer', 'feedback', 'closing', 'escalation', 'unknown'}
    
    # 消息内容最大长度
    CONTENT_MAX_LENGTH = 10000
    
    # 满意度评分范围
    SATISFACTION_MIN = 0
    SATISFACTION_MAX = 5

    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条客户对话记录

        Args:
            record: 原始记录
            llm_client: LLM客户端（可选，用于意图识别）

        Returns:
            清洗后的记录，如无法清洗返回None
        """
        if not record:
            return None
        
        # 1. 验证并清洗主键
        conversation_id = record.get('conversation_id', '').strip()
        if not conversation_id:
            logger.debug("对话ID为空，记录被删除")
            return None
        
        cleaned = {'conversation_id': conversation_id}
        
        # 2. 清洗客户ID（缺失使用UNKNOWN）
        customer_id = record.get('customer_id', '').strip()
        if not customer_id:
            customer_id = 'UNKNOWN'
        cleaned['customer_id'] = customer_id
        
        # 3. 清洗服务人员ID（缺失使用SYSTEM）
        service_id = record.get('service_id', '').strip()
        if not service_id:
            service_id = 'SYSTEM'
        cleaned['service_id'] = service_id
        
        # 4. 验证并清洗消息内容（必填）
        message_content = record.get('message_content', '').strip()
        if not message_content:
            logger.debug(f"消息内容为空，记录被删除：{conversation_id}")
            return None
        
        # 文本清洁（去emoji、去HTML、保留URL）
        message_content = StringUtils.clean_text(
            message_content,
            remove_html=True,
            remove_urls=False,  # 对话中的URL可能有用
            remove_emoji=True,
            remove_mentions=False,
            max_length=self.CONTENT_MAX_LENGTH
        )
        
        cleaned['message_content'] = message_content
        
        # 5. 清洗消息类型
        message_type = record.get('message_type', 'unknown').strip().lower()
        if message_type not in self.VALID_MESSAGE_TYPES:
            message_type = 'unknown'
        cleaned['message_type'] = message_type
        
        # 6. 清洗消息时间（标准化）
        message_time = record.get('message_time', '')
        if message_time:
            try:
                message_time = TimeUtils.standardize_timestamp(message_time)
                if not message_time:
                    message_time = None
            except Exception as e:
                logger.debug(f"时间转换失败：{record.get('message_time')}，错误：{e}")
                message_time = None
        else:
            message_time = None
        
        cleaned['message_time'] = message_time
        
        # 7. 处理其他可选字段
        # 对话时长（秒）
        try:
            duration_seconds = int(record.get('duration_seconds', 0))
            duration_seconds = max(0, duration_seconds)
        except (ValueError, TypeError):
            duration_seconds = 0
        cleaned['duration_seconds'] = duration_seconds
        
        # 满意度评分（0-5）
        satisfaction_score = record.get('satisfaction_score')
        if satisfaction_score is not None and satisfaction_score != '':
            try:
                satisfaction_score = int(float(satisfaction_score))
                # 限制范围
                satisfaction_score = max(self.SATISFACTION_MIN, min(self.SATISFACTION_MAX, satisfaction_score))
            except (ValueError, TypeError):
                satisfaction_score = None
        else:
            satisfaction_score = None
        cleaned['satisfaction_score'] = satisfaction_score
        
        # 是否已解决
        try:
            is_resolved = bool(record.get('is_resolved', False))
        except (ValueError, TypeError):
            is_resolved = False
        cleaned['is_resolved'] = is_resolved
        
        # 8. 可选LLM意图识别
        if llm_client:
            try:
                intent = llm_client.identify_intent(message_content)
                cleaned['intent_category'] = intent.get('category')
                cleaned['intent_confidence'] = intent.get('confidence')
            except Exception as e:
                logger.warning(f"LLM意图识别失败：{e}")
                cleaned['intent_category'] = None
                cleaned['intent_confidence'] = None
        else:
            cleaned['intent_category'] = None
            cleaned['intent_confidence'] = None
        
        # 9. 标记清洗状态
        cleaned['is_cleaned'] = True
        cleaned['clean_time'] = None  # 由存储层填充
        
        return cleaned
