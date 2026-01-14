# -*- coding: utf-8 -*-
"""
客户对话数据清洗器

业务类型_14：CUSTOMER_DIALOG
清洗规则：对话去重、消息清洁、情感分析、主题分类
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import re
import hashlib
from datetime import datetime, date, timedelta

from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.validation import Validator
from src.utils.statistics import Statistics
from src.cleaner.base_cleaner import BaseCleaner
from src.ai_service.api_client import get_llm_client
from src.db_service.db_manager import query_records

logger = get_logger(__name__)


class CustomerDialogCleaner(BaseCleaner):
    """
    客户对话清洗器
    
    清洗目标：
    1. 会话结构扁平化（一消息一记录）
    2. 消息内容清洁（去HTML、Emoji、Spam）
    3. 身份与平台标准化
    4. 核心字段准确度评估
    5. 质量分计算
    """
    
    BUSINESS_TYPE_ID = 'CUSTOMER_DIALOG'
    PRIMARY_KEY = 'id'
    CORE_FIELDS = ['merchant_name', 'customer_name', 'agent_name', 'message_type', 'message_content', 'message_time', 'platform']
    
    # 表头映射
    HEADER_MAPPING = {
        '会话ID': 'conversation_id',
        'conversation_id': 'conversation_id',
        '商户名称': 'merchant_name',
        'merchant_name': 'merchant_name',
        '客户名称': 'customer_name',
        'customer_name': 'customer_name',
        '客服名称': 'agent_name',
        'agent_name': 'agent_name',
        '消息内容': 'message_content',
        'content': 'message_content',
        'message_content': 'message_content',
        '消息时间': 'message_time',
        'message_time': 'message_time',
        'timestamp': 'message_time',
        '平台': 'platform',
        'platform': 'platform'
    }
    
    # 清洗常量
    MAX_MESSAGE_LEN = 5000
    SPAM_PATTERNS = [
        r'(.)\1{10,}', # 连续重复字符
        r'加微信|加V|联系电话|客服电话', # 敏感引导(根据业务调整)
    ]
    
    def __init__(self):
        super().__init__()

    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        BaseCleaner要求的抽象方法。
        由于CustomerDialog是1对多关系，实际逻辑在_clean_session中处理。
        此方法仅返回None以避开基类默认循环。
        """
        return None

    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = True) -> Dict[str, Any]:
        """
        清洗客户对话数据
        支持两种输入结构：
        1. 嵌套结构 (JSON): [{'conversation_id': '...', 'messages': [...]}, ...]
        2. 扁平结构 (Excel/CSV): [{'conversation_id': '...', 'message_content': '...'}, ...]
        """
        cleaner = CustomerDialogCleaner()
        all_flattened_records = []
        errors = []
        llm_client = get_llm_client() if enable_llm else None
        
        # 识别并处理结构类型
        processed_sessions = []
        if records and 'messages' not in records[0] and ('conversation_id' in records[0] or '会话ID' in records[0] or 'message_content' in records[0]):
            # 扁平结构：按会话ID分组重构
            logger.info("检测到扁平数据结构，正在重构会话...")
            sessions_map = {}
            for rec in records:
                # 统一获取并处理字段，防止 None/NaN
                def get_val(r, *keys):
                    for k in keys:
                        v = r.get(k)
                        if v is not None and str(v).lower() != 'nan':
                            return str(v).strip()
                    return ''

                conv_id = get_val(rec, 'conversation_id', '会话ID') or 'default_conv'
                if conv_id not in sessions_map:
                    # 提取会话级字段
                    sessions_map[conv_id] = {
                        'conversation_id': conv_id,
                        'merchant_name': get_val(rec, 'merchant_name', '商户名称'),
                        'customer_name': get_val(rec, 'customer_name', '客户名称'),
                        'agent_name': get_val(rec, 'agent_name', '客服名称'),
                        'platform': get_val(rec, 'platform', '平台'),
                        'product_name': get_val(rec, 'product_name', '产品名称'),
                        'data_crawl_date': get_val(rec, 'data_crawl_date', '抓取日期'),
                        'messages': []
                    }
                
                # 提取消息级字段
                msg = {
                    'sender': get_val(rec, 'sender', '发送者') or 'Unknown',
                    'content': get_val(rec, 'message_content', '消息内容', 'content'),
                    'timestamp': get_val(rec, 'message_time', '消息时间', 'timestamp'),
                    'agent_type': get_val(rec, 'agent_type', '客服类型')
                }
                sessions_map[conv_id]['messages'].append(msg)
            processed_sessions = list(sessions_map.values())
        else:
            # 已经是嵌套结构
            processed_sessions = records

        original_session_count = len(processed_sessions)
        
        for idx, session in enumerate(processed_sessions):
            try:
                # 扁平化清洗：一个Session包含多个Messages
                session_records = cleaner._clean_session(session, llm_client)
                if session_records:
                    all_flattened_records.extend(session_records)
            except Exception as e:
                errors.append(f"会话[{idx}]清洗失败：{e}")
                logger.warning(f"会话清洗失败：{e}")
        
        # 计算统计信息 (以消息为单位)
        dedup_rate = Statistics.calculate_dedup_rate(all_flattened_records, 'knowledge_id')
        missing_rate = Statistics.calculate_missing_rate(all_flattened_records)
        
        logger.info(f"客户对话清洗完成：产生 {len(all_flattened_records)} 条消息记录，源会话数：{original_session_count}")
        
        return {
            'success': True,
            'business_type_id': cleaner.BUSINESS_TYPE_ID,
            'original_count': original_session_count,
            'cleaned_count': len(all_flattened_records),
            'records': all_flattened_records,
            'statistics': {
                'dedup_rate': dedup_rate,
                'missing_rate': missing_rate,
                'errors': errors
            }
        }

    def _clean_session(self, session: Dict[str, Any], llm_client: Any = None) -> List[Dict[str, Any]]:
        """
        清洗单个会话，将其拆分为多条消息记录
        """
        flattened_records = []
        
        # 1. 提取会话级字段
        conversation_id = str(session.get('conversation_id') or '').strip()
        order_id = str(session.get('order_id') or '').strip()
        
        # 边界处理：如果缺少 ID，尝试生成一个唯一的会话标识
        if not conversation_id:
            # 绝不使用脱敏名称作为种子！
            # 使用 商户 + 平台 + 订单 + 消息摘要(取第一条消息) 作为唯一特征
            first_msg_content = ""
            if session.get('messages'):
                first_msg_content = str(session.get('messages')[0].get('content', ''))
            
            raw_id_seed = f"{session.get('merchant_name')}|{session.get('platform')}|{order_id}|{first_msg_content[:100]}"
            conversation_id = hashlib.md5(raw_id_seed.encode()).hexdigest()
            logger.info(f"生成独立会话标识: {conversation_id}")
            
        merchant_name_raw = str(session.get('merchant_name') or '').strip()
        platform_raw = str(session.get('platform') or '').strip()
        
        # 边界处理：互补推理
        if not merchant_name_raw and platform_raw and conversation_id.startswith('WX'):
            platform_raw = '微信'

        messages = session.get('messages', [])
        
        if not isinstance(messages, list) or not messages:
            logger.warning(f"会话 {conversation_id} 消息为空或格式错误")
            return []

        # 尝试从消息中提取参与者 (如果 Session 级缺失)
        inferred_customer = None
        inferred_agent = None
        for msg in messages:
            sender = msg.get('sender', '')
            if not sender: continue
            # 这里传递商户原始名称 merchant_name_raw 参与推理
            m_type = self._infer_message_type(sender, '', merchant_name_raw or '', 'UnknownCustomer')
            if msg.get('agent_type') or m_type == '客服回复':
                if not inferred_agent: inferred_agent = sender
            elif m_type == '客户消息':
                if not inferred_customer: inferred_customer = sender
            if inferred_customer and inferred_agent: break

        customer_name_raw = str(session.get('customer_name') or inferred_customer or '匿名客户').strip()
        agent_name_raw = str(session.get('agent_name') or inferred_agent or '在线客服').strip()

        # 尝试从数据库补充标准商户名
        merchant_name = self._standardize_merchant_from_db(merchant_name_raw)
        # 平台标准化
        platform = self._standardize_platform(platform_raw or '未知')
        # 客户名称 (不再进行脱敏)
        customer_name = customer_name_raw
        # 客服名称标准化
        agent_name = self._standardize_agent(agent_name_raw)
        
        # --- 身份标识处理 ---
        # 客户名称从平台下载时已脱敏，完全不可信。
        # 核心逻辑：订单号 > 对话中提取的关键信息(手机号/账号) > 会话ID(确保不碰撞)
        
        # 从对话内容中尝试提取手机号作为关键信息 (简单正则示例)
        key_info_from_content = ''
        messages = session.get('messages', [])
        for m in messages:
            content = str(m.get('content', ''))
            phone_match = re.search(r'1[3-9]\d{9}', content)
            if phone_match:
                key_info_from_content = phone_match.group()
                break

        if order_id:
            # 1. 优先使用订单号
            user_id_seed = f"ORDER|{merchant_name}|{platform}|{order_id}"
        elif key_info_from_content:
            # 2. 其次使用提取出的唯一特征
            user_id_seed = f"INFO|{merchant_name}|{platform}|{key_info_from_content}"
        else:
            # 3. 兜底策略：使用生成的会话ID。保证不同人绝不会因为脱敏名字相同而撞车。
            # 虽然无法跨会话识别散客，但保证了数据的“物理隔离”。
            user_id_seed = f"SESSION|{conversation_id}"
            
        user_id = hashlib.md5(user_id_seed.encode()).hexdigest()[:20]

        # --- 客户身份边界情况处理 ---
        # 2. 尝试通过订单号查询数据库，验证或修正客户身份
        if order_id:
            db_customer_info = self._query_customer_info_from_db(order_id, None, merchant_name, customer_name)
            if db_customer_info:
                # 如果数据库中的客户信息与当前推断的不一致，需要评估哪个更可信
                db_user_id = db_customer_info.get('user_id')
                db_customer_name = db_customer_info.get('customer_name')
                
                # 策略：如果user_id匹配，则优先使用数据库中的客户名
                if user_id and db_user_id == user_id:
                    # 但注意，数据库中的名字可能也是脱敏的，所以不一定完全覆盖
                    # 这里可以记录一个日志，或根据需要调整
                    logger.debug(f"会话 {conversation_id} 的 user_id 与数据库匹配，客户名: {db_customer_name}")
                # 策略：如果订单号匹配，且订单关联的客户名与当前不一致
                if order_id and db_customer_name and db_customer_name != customer_name:
                    logger.info(f"会话 {conversation_id} 的订单 {order_id} 关联的客户名与当前推断不一致: '{customer_name}' vs '{db_customer_name}'")
                    # 这里可以决定是否更新 customer_name 或 user_id，或标记为待审核
                    # 暂时保持原有逻辑，但增加一个准确度评估字段来记录这个发现
                    cleaned['customer_name_anal_info'] = f"{cleaned.get('customer_name_anal_info', '')} | 订单关联客户名: {db_customer_name}"

        product_name_session = session.get('product_name')
        data_crawl_date = self._parse_date(session.get('data_crawl_date'))
        
        # 2. 逐条清洗消息
        seen_messages = set() # 会话内去重
        for m_idx, msg in enumerate(messages):
            content_raw = str(msg.get('content', '')).strip()
            timestamp_raw = str(msg.get('timestamp', '') or msg.get('message_time', '')).strip()
            
            # 会话内去重
            msg_fingerprint = hashlib.md5(f"{content_raw}_{timestamp_raw}".encode()).hexdigest()
            if msg_fingerprint in seen_messages:
                continue
            seen_messages.add(msg_fingerprint)

            cleaned_msg = self._clean_single_message(
                msg, 
                conversation_id, 
                merchant_name, 
                customer_name, 
                agent_name, 
                platform, 
                user_id,
                product_name_session,
                m_idx
            )
            
            if cleaned_msg:
                # 附加会话级的公共属性
                cleaned_msg['data_crawl_date'] = data_crawl_date
                cleaned_msg['data_update_time'] = self._parse_datetime(session.get('update_time'))
                
                # 确保所有记录都有相同的字段，即使是 None (为了数据库批量导入)
                cleaned_msg['resolution_time'] = None
                cleaned_msg['satisfaction'] = None
                
                # 最后一条消息附加状态和评价
                if m_idx == len(messages) - 1:
                    cleaned_msg['resolution_time'] = session.get('resolution_time')
                    cleaned_msg['satisfaction'] = session.get('satisfaction')
                    cleaned_msg['conversation_status'] = session.get('conversation_status', '已结束')
                else:
                    cleaned_msg['conversation_status'] = '进行中'
                
                flattened_records.append(cleaned_msg)
                
        return flattened_records

    def _clean_single_message(self, msg: Dict[str, Any], conv_id: str, merchant: str, customer: str, agent: str, platform: str, user_id: str, product_name_session: str, msg_index: int) -> Optional[Dict[str, Any]]:
        """
        清洗单条消息并构建数据库记录格式
        """
        content_raw = msg.get('content', '').strip()
        if not content_raw:
            return None
            
        # 1. 文本清洁 (不再进行脱敏)
        # 基础清洁
        content = StringUtils.clean_text(content_raw, remove_urls=False)
        content = StringUtils.truncate_text(content, self.MAX_MESSAGE_LEN)
        
        # 垃圾内容检测
        is_spam = 0
        for pattern in self.SPAM_PATTERNS:
            if re.search(pattern, content):
                is_spam = 1
                break

        # 2. 身份与类型提取
        sender_raw = msg.get('sender', '').strip()
        m_type = self._infer_message_type(sender_raw, content, merchant, customer)
        
        # 提取消息级的属性
        msg_agent_type = msg.get('agent_type')
        
        if m_type == '客服回复':
            # 如果是客服回复，sender_raw 就是具体的客服名
            current_agent = self._standardize_agent(sender_raw, msg_agent_type)
        else:
            # 如果是客户消息，保留会话级客服名（或留空，视数据库需求而定）
            current_agent = agent 

        # 3. 构建记录
        cleaned = {
            'conversation_id': conv_id,
            'user_id': user_id or 'unknown',
            'merchant_name': merchant,
            'customer_name': customer,
            'agent_name': current_agent,
            'platform': platform,
            'message_content': content,
            'product_name': product_name_session,
            'version': 1,
            'is_valid': True,
            'data_status': 'valid',
            'validity_reason': None
        }
        
        # 4. 消息时间处理
        m_time = self._parse_datetime(msg.get('timestamp') or msg.get('message_time'))
        if not m_time:
            logger.warning(f"消息缺失时间戳: {conv_id}")
            return None
        cleaned['message_time'] = m_time
        cleaned['message_type'] = m_type
        
        # 5. 情感分析
        cleaned['sentiment'] = self._simple_sentiment_analysis(content)
        
        # --- 6. 准确度评估 (严谨模型) ---
        # 评估公式: (reliability * 0.4) + (consistency * 0.3) + (validation * 0.3)
        
        # 商家评估
        rel = 95 if merchant != '未知商家' else 40
        cons = 100 if merchant in content or not merchant.startswith('未知') else 60
        val = 90 # 匹配了标准库
        cleaned['merchant_name_anal'], cleaned['merchant_name_anal_info'] = self._evaluate_accuracy(rel, cons, val, "商家名匹配及互补推理")
        
        # 客户评估
        rel = 90 if customer != '匿名客户' else 50
        cleaned['customer_name_anal'], cleaned['customer_name_anal_info'] = self._evaluate_accuracy(rel, 100, 80, "客户名称提取")
        
        # 客服评估
        # 如果消息直接带有 agent_type 或者 sender 不是商户全称，说明评估准确度更高
        rel = 95 if (msg_agent_type or sender_raw != merchant) else 80
        cons = 100 if current_agent != '在线客服' else 60
        cleaned['agent_name_anal'], cleaned['agent_name_anal_info'] = self._evaluate_accuracy(rel, cons, 85, "客服身份标准化与消息级匹配")
        
        # 消息类型评估
        rel = 98 if msg_agent_type else 90
        cons = 100 if (cleaned['message_type'] == '客服回复' and current_agent != '在线客服') else 70
        cleaned['message_type_anal'], cleaned['message_type_anal_info'] = self._evaluate_accuracy(rel, cons, 85, "发送者身份与内容特征推导")
        
        # 内容评估
        rel = 98
        cons = 100 if len(content) > 2 else 50
        val = 100 if is_spam == 0 else 40
        cleaned['message_content_anal'], cleaned['message_content_anal_info'] = self._evaluate_accuracy(rel, cons, val, "文本清洁及垃圾内容过滤")
        
        # 时间评估
        rel = 95
        cleaned['message_time_anal'], cleaned['message_time_anal_info'] = self._evaluate_accuracy(rel, 100, 95, "时间戳标准化")
        
        # 平台评估
        rel = 100 if platform != '其他' else 50
        cleaned['platform_anal'], cleaned['platform_anal_info'] = self._evaluate_accuracy(rel, 100, 100, "平台映射规范化")
        
        # --- 7. 最终质量分与状态 ---
        core_scores = [
            cleaned['merchant_name_anal'], cleaned['customer_name_anal'], 
            cleaned['agent_name_anal'], cleaned['message_type_anal'],
            cleaned['message_content_anal'], cleaned['message_time_anal'],
            cleaned['platform_anal']
        ]
        q_score = sum(core_scores) / len(core_scores)
        
        # 惩罚项
        if is_spam: q_score -= 20
        if not sender_raw: q_score -= 10
        if len(content) < 2: q_score -= 10
        
        cleaned['quality_score'] = max(0, min(100, int(q_score)))
        
        if cleaned['quality_score'] < 50:
            cleaned['data_status'] = 'invalid'
            cleaned['is_valid'] = False
            cleaned['validity_reason'] = '质量分数过低'
        elif cleaned['quality_score'] < 75:
            cleaned['data_status'] = 'pending_review'
            
        cleaned['cleaned_at'] = datetime.now()
        
        return cleaned

    def _simple_sentiment_analysis(self, text: str) -> str:
        pos_words = ['好', '满意', '谢谢', '感谢', '赞', '快', '正品']
        neg_words = ['差', '慢', '投诉', '退货', '假货', '坏', '垃圾']
        
        pos_count = sum(1 for w in pos_words if w in text)
        neg_count = sum(1 for w in neg_words if w in text)
        
        if neg_count > pos_count: return '负面'
        if pos_count > neg_count: return '正面'
        return '中立'

    def _standardize_merchant_from_db(self, name: str) -> str:
        """
        通过查询数据库来标准化商户名称
        这是处理同义词、别名的关键方法
        """
        name = str(name).strip()
        if not name:
            return '未知商家'
        
        # 尝试查询 ec_product_info 表中的 shop_name 字段，寻找匹配项
        try:
            # 使用模糊查询或精确查询，取决于业务需求
            # 这里先尝试精确匹配，再尝试模糊匹配
            exact_result = query_records(
                "SELECT DISTINCT shop_name FROM ec_product_info WHERE shop_name = :name LIMIT 1",
                {"name": name}
            )
            
            if exact_result:
                return exact_result[0]['shop_name']
            
            # 如果精确匹配失败，尝试模糊匹配（包含）
            fuzzy_result = query_records(
                "SELECT DISTINCT shop_name FROM ec_product_info WHERE shop_name LIKE :pattern LIMIT 1",
                {"pattern": f"%{name}%"}
            )
            
            if fuzzy_result:
                return fuzzy_result[0]['shop_name']
                
            # 如果数据库中没有匹配项，则返回原名称或进行其他处理
            # 为了通用性，这里直接返回原名，但实际业务中可能需要更复杂的逻辑
            return name
            
        except Exception as e:
            logger.warning(f"查询数据库标准化商户名失败 ({name}): {e}")
            # 查询失败时，返回原名称
            return name

    def _standardize_platform(self, platform: str) -> str:
        p = str(platform).strip().lower()
        mapping = {
            'pdd': '拼多多',
            'pinduoduo': '拼多多',
            '拼多多': '拼多多',
            'tb': '淘宝',
            'taobao': '淘宝',
            '淘宝': '淘宝',
            'jd': '京东',
            'jingdong': '京东',
            '京东': '京东',
            'wx': '微信',
            'wechat': '微信',
            '微信': '微信'
        }
        return mapping.get(p, '未知')

    def _standardize_agent(self, name: str, agent_type: Optional[str] = None) -> str:
        name = str(name).strip()
        if not name or name == '在线客服':
            return '在线客服'
        
        # 智能助手识别关键词
        smart_keywords = ['机器人', '智能', 'AI', '机器', '智能助手', '机器助手', 'AI助手']
        
        # 检查是否为智能助手 (检查 agent_type 或 name)
        is_smart = False
        if agent_type and any(kw in str(agent_type) for kw in smart_keywords):
            is_smart = True
        elif any(kw in name for kw in smart_keywords):
            is_smart = True
            
        if is_smart:
            # 统一标准化：移除原有的标识并添加统一的 (智能助手) 后缀
            clean_name = name
            for kw in smart_keywords:
                clean_name = clean_name.replace(f'({kw})', '').replace(f'（{kw}）', '').replace(kw, '')
            
            clean_name = clean_name.strip(' ()（）')
            return f"{clean_name}(智能助手)" if clean_name else "智能助手"
            
        return name

    def _infer_message_type(self, sender: str, content: str, merchant: str, customer: str) -> str:
        sender = sender.lower()
        # 客服关键词
        agent_keywords = ['客服', '售后', '助手', '小妹', '掌柜', '专员', '技术支持']
        
        # 如果 sender 包含商户名的关键部分，认为是客服
        if merchant.lower() in sender or any(kw in sender for kw in agent_keywords):
            return '客服回复'
        if 'system' in sender or '系统' in sender:
            return '系统消息'
        return '客户消息'

    def _parse_datetime(self, val: Any) -> Optional[datetime]:
        if not val: return None
        if isinstance(val, datetime): return val
        val_str = str(val).strip()
        try:
            return datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S')
        except:
            # standardize_timestamp 返回字符串，需要转回 datetime
            standardized = TimeUtils.standardize_timestamp(val_str)
            if standardized:
                try:
                    return datetime.strptime(standardized, '%Y-%m-%d %H:%M:%S')
                except:
                    return None
            return None

    def _parse_date(self, val: Any) -> date:
        dt = self._parse_datetime(val)
        if isinstance(dt, datetime):
            return dt.date()
        return date.today()

    def _query_customer_info_from_db(self, order_id: Optional[str], user_id: Optional[str], merchant_name: str, customer_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        通过订单号或客户名称查询数据库，获取客户历史信息以辅助判断。
        注意：抓取阶段通常没有 user_id，所以主要依靠客户名或订单号进行回溯。
        """
        try:
            # 1. 如果提供了订单号，尝试查询该订单对应的历史客户信息
            if order_id:
                sql = """
                SELECT DISTINCT user_id, customer_name FROM customer_conversation 
                WHERE merchant_name = :merchant AND message_content LIKE :order_pattern 
                ORDER BY message_time DESC LIMIT 1
                """
                params = {"merchant": merchant_name, "order_pattern": f"%{order_id}%"}
                result = query_records(sql, params)
                if result:
                    logger.debug(f"通过 order_id {order_id} 追溯到历史客户信息: {result[0]}")
                    return result[0]
            
            # 2. 如果没有订单号，或者订单查询无果，则根据 商家名+客户名 查找其在库中的 user_id
            if customer_name and customer_name != '匿名客户':
                sql = """
                SELECT DISTINCT user_id, customer_name FROM customer_conversation 
                WHERE merchant_name = :merchant AND customer_name = :customer 
                LIMIT 1
                """
                params = {"merchant": merchant_name, "customer": customer_name}
                result = query_records(sql, params)
                if result:
                    logger.debug(f"通过客户名称 '{customer_name}' 关联到历史 user_id: {result[0].get('user_id')}")
                    return result[0]
            
            return None
        
        except Exception as e:
            logger.warning(f"查询数据库获取历史客户信息失败: {e}")
            return None
