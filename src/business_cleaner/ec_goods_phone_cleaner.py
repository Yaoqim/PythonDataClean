# -*- coding: utf-8 -*-
"""
电商商品数据清洗器

业务类型_1：EC_GOODS_PHONE
清洗规则：商品字段标准化、价格数值化、销量有效性验证
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import hashlib
import json
from datetime import datetime, date, timedelta

from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.validation import Validator
from src.utils.statistics import Statistics
from src.cleaner.base_cleaner import BaseCleaner

logger = get_logger(__name__)


class ECGoodsPhoneCleaner(BaseCleaner):
    """
    电商商品清洗器
    
    清洗目标：
    1. 商品名称去重、去HTML、截断
    2. 价格转换为浮点数、范围验证
    3. 销量有效性检查
    4. 分类标准化
    5. 核心字段准确度评估
    """
    
    # 配置
    BUSINESS_TYPE_ID = 'EC_GOODS_PHONE'
    PRIMARY_KEY = 'product_id'
    REQUIRED_FIELDS = ['product_id', 'title', 'price', 'source_platform']
    
    # 核心字段列表
    CORE_FIELDS = ['title', 'price', 'currency_code', 'shop_name', 'source_platform']
    
    # 表头映射：支持多种原始表头转换为标准字段名
    HEADER_MAPPING = {
        '商品ID': 'product_id',
        '商品id': 'product_id',
        'product_id': 'product_id',
        '商品名称': 'title',
        '标题': 'title',
        'title': 'title',
        '价格': 'price',
        'price': 'price',
        '店铺': 'shop_name',
        'shop_name': 'shop_name',
        '平台': 'source_platform',
        'source_platform': 'source_platform',
        'currency_code': 'currency_code',
        '币种': 'currency_code'
    }
    
    MAX_PRODUCT_NAME_LEN = 200
    MIN_PRICE = 0.01
    MAX_PRICE = 10000000
    MAX_SALES = 99999999
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        """
        清洗电商商品数据 (保持与编排器兼容的静态方法接口，内部实例化并调用基类方法)
        """
        cleaner = ECGoodsPhoneCleaner()
        cleaned_records, stats = cleaner.clean_records_all(records, enable_llm)
        
        return {
            'success': True,
            'business_type_id': cleaner.BUSINESS_TYPE_ID,
            'original_count': stats['original_count'],
            'cleaned_count': stats['cleaned_count'],
            'records': cleaned_records,
            'statistics': {
                'dedup_rate': Statistics.calculate_dedup_rate(cleaned_records, 'product_id'),
                'missing_rate': Statistics.calculate_missing_rate(cleaned_records),
                'errors': [] # 简化处理
            }
        }

    def clean_records_all(self, records: List[Dict[str, Any]], enable_llm: bool = False) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """调用基类清洗方法"""
        return super().clean(records, None)

    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条记录
        """
        cleaned = {}
        
        # 1. 枢纽字段: product_id
        product_id = str(record.get('product_id', '')).strip()
        if not product_id:
            logger.warning("缺少product_id，跳过记录")
            return None
        cleaned['product_id'] = product_id
        
        # 2. 获取原始数据
        source_platform = str(record.get('source_platform') or record.get('platform') or '').strip().lower()
        title_raw = record.get('title', '') or record.get('product_name', '')
        title = StringUtils.clean_text(str(title_raw).strip())
        price_raw = record.get('price')
        shop_name_raw = record.get('shop_name')
        
        # --- 3. 缺失补充逻辑 ---
        is_supplemented = False
        db_info = {}
        if not source_platform or not title or price_raw is None:
            db_info = self._supplement_from_db(product_id)
            if db_info:
                if not source_platform:
                    source_platform = db_info.get('source_platform', '').lower()
                    is_supplemented = True
                if not title:
                    title = db_info.get('title', '')
                    is_supplemented = True
                if price_raw is None or str(price_raw).strip() == '':
                    price_raw = db_info.get('price')
                    is_supplemented = True
                if not shop_name_raw:
                    shop_name_raw = db_info.get('shop_name')

        # 4. 关键字段校验 (舍弃逻辑)
        if not source_platform or not title:
            logger.warning(f"缺少关键字段(platform/title)且无法补充，跳过记录: {product_id}")
            return None
            
        cleaned['source_platform'] = source_platform
        
        # 5. 知识ID处理 (打标阶段产生，暂设None)
        cleaned['knowledge_id'] = None
        
        # 6. 核心字段: title
        is_official = 0
        if "【官方旗舰店】" in title or "官方旗舰店" in title:
            is_official = 1
            title = title.replace("【官方旗舰店】", "").replace("官方旗舰店", "").strip()
        cleaned['title'] = StringUtils.truncate_text(title, 200)
        cleaned['is_official'] = is_official
        
        # 7. 核心字段: price
        price = self._parse_price(price_raw)
        price_status = "正常"
        if price is None:
            # 如果解析失败且是补充的，或者原始就缺失
            price_status = "价格非最新/缺失"
            # 即使缺失也保留，除非是业务要求的必填(目前REQUIRED_FIELDS含price，但根据用户新要求，不舍弃)
            cleaned['price'] = 0.0 # 填充默认值
        else:
            cleaned['price'] = price
        
        # 8. 核心字段: currency_code
        currency_code = str(record.get('currency_code') or db_info.get('currency_code') or 'CNY').strip().upper()
        if not currency_code or len(currency_code) != 3:
            currency_code = 'CNY'
        cleaned['currency_code'] = currency_code
        
        # 9. 核心字段: shop_name
        shop_name = str(shop_name_raw or '未知').strip()
        cleaned['shop_name'] = shop_name[:100]
        
        # --- 准确度评估 ---
        # title 评估
        rel = 95 if record.get('title') else (80 if db_info.get('title') else 50)
        cons = 100 if len(cleaned['title']) > 5 else 70
        val = 90
        cleaned['title_anal'], cleaned['title_anal_info'] = self._evaluate_accuracy(rel, cons, val, "API获取" if rel == 95 else ("DB补充" if rel == 80 else "提取"))
        
        # price 评估
        rel = 95 if isinstance(record.get('price'), (int, float)) else (80 if db_info.get('price') else 40)
        cons = 100 if self.MIN_PRICE <= cleaned['price'] <= self.MAX_PRICE else 50
        val = 85
        cleaned['price_anal'], cleaned['price_anal_info'] = self._evaluate_accuracy(rel, cons, val, f"{price_status}" if rel < 95 else "数值")
        
        # currency_code 评估
        cleaned['currency_code_anal'], cleaned['currency_code_anal_info'] = self._evaluate_accuracy(95, 100, 100, "默认/识别")
        
        # shop_name 评估
        rel = 90 if record.get('shop_name') else (70 if db_info.get('shop_name') else 50)
        cleaned['shop_name_anal'], cleaned['shop_name_anal_info'] = self._evaluate_accuracy(rel, 100, 80, "原始字段" if rel == 90 else ("DB补充" if rel == 70 else "默认填充"))
        
        # source_platform 评估
        rel = 100 if record.get('source_platform') else (85 if db_info.get('source_platform') else 60)
        cleaned['source_platform_anal'], cleaned['source_platform_anal_info'] = self._evaluate_accuracy(rel, 100, 100, "系统预设" if rel == 100 else "DB补充")
        
        # --- 其他业务字段 ---
        # original_price
        orig_price_str = record.get('original_price')
        if orig_price_str:
            cleaned['original_price'] = self._parse_price(orig_price_str)
        
        # brand
        brand = str(record.get('brand', '')).strip()
        cleaned['brand'] = brand or None
        
        # spec_params
        spec_params = record.get('spec_params')
        if isinstance(spec_params, str):
            try:
                cleaned['spec_params'] = json.loads(spec_params)
            except:
                cleaned['spec_params'] = {"raw": spec_params}
        elif isinstance(spec_params, dict):
            cleaned['spec_params'] = spec_params
        else:
            cleaned['spec_params'] = None
            
        # sales_volume
        sales_str = record.get('sales_volume') or record.get('sales', '')
        cleaned['sales_volume'] = self._parse_sales(sales_str) or 0
        
        # comment_count
        comm_str = record.get('comment_count')
        cleaned['comment_count'] = self._parse_sales(comm_str) or 0
        
        # rating
        rating_str = record.get('rating', 0)
        cleaned['rating'] = self._parse_rating(rating_str) or 0.0
        
        # good_rate
        good_rate = record.get('good_rate', 0)
        try:
            cleaned['good_rate'] = float(str(good_rate).replace('%', ''))
        except:
            cleaned['good_rate'] = 0.0
            
        # shop_id
        cleaned['shop_id'] = str(record.get('shop_id', '')).strip() or None
        
        # listing_time & update_time (数据修改的时间)
        for time_field in ['listing_time', 'update_time']:
            val = record.get(time_field)
            if val:
                cleaned[time_field] = self._parse_datetime(val)
        
        # 公共必填字段
        # 使用抓取阶段提供的抓取日期
        cleaned['data_crawl_date'] = self._parse_date(record.get('data_crawl_date'))
        cleaned['last_updated_at'] = datetime.now()
        cleaned['is_cleaned'] = 1
        cleaned['clean_time'] = datetime.now()
        cleaned['data_status'] = 'normal'
        cleaned['version'] = 1
        
        # 质量总分 (平均核心字段评分)
        core_anal_scores = [cleaned['title_anal'], cleaned['price_anal'], cleaned['currency_code_anal'], cleaned['shop_name_anal'], cleaned['source_platform_anal']]
        cleaned['quality_score'] = sum(core_anal_scores) / len(core_anal_scores)
        
        return cleaned

    def _supplement_from_db(self, product_id: str) -> Dict[str, Any]:
        """从数据库补充缺失信息"""
        try:
            from src.db_service.db_manager import query_records
            # 尝试查找已存在的同一商品记录
            results = query_records(
                "SELECT source_platform, title, shop_name, price, currency_code FROM ec_product_info WHERE product_id = :pid ORDER BY update_time DESC LIMIT 1",
                {"pid": product_id}
            )
            return results[0] if results else {}
        except Exception as e:
            # 记录错误但不中断流程
            logger.debug(f"尝试从DB补充数据失败({product_id}): {e}")
            return {}

    def _parse_datetime(self, val: Any) -> Optional[datetime]:
        if not val: return None
        if isinstance(val, datetime): return val
        val_str = str(val).strip()
        
        # 处理相对时间
        now = datetime.now()
        if "小时前" in val_str:
            try:
                hours = int(re.search(r'(\d+)', val_str).group(1))
                return now - timedelta(hours=hours)
            except: pass
        elif "分钟前" in val_str:
            try:
                minutes = int(re.search(r'(\d+)', val_str).group(1))
                return now - timedelta(minutes=minutes)
            except: pass
        elif "天前" in val_str:
            try:
                days = int(re.search(r'(\d+)', val_str).group(1))
                return now - timedelta(days=days)
            except: pass
        elif val_str == "昨天":
            return now - timedelta(days=1)
        elif val_str == "前天":
            return now - timedelta(days=2)
        elif "刚刚" in val_str:
            return now

        try:
            # 处理 ISO 格式
            if 'T' in val_str:
                return datetime.fromisoformat(val_str.replace('Z', '+00:00'))
            return datetime.strptime(val_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.strptime(val_str, '%Y-%m-%d')
            except:
                try:
                    # 处理 "Jan 1, 2024" 格式
                    return datetime.strptime(val_str, '%b %d, %Y')
                except:
                    return None

    def _parse_date(self, val: Any) -> date:
        dt = self._parse_datetime(val)
        return dt.date() if dt else date.today()

    @staticmethod
    def _parse_price(price_str: Any) -> Optional[float]:
        """
        解析价格字符串
        
        支持格式：
        - "99.99"
        - "99"
        - "¥99.99"
        - "$99.99"
        - "£45.00"
        - "Negotiable" -> None
        """
        if not price_str:
            return None
        
        price_str = str(price_str).strip()
        
        # 如果是纯字母或特殊说明，返回 None
        if re.search(r'[a-zA-Z]{3,}', price_str) and not any(c.isdigit() for c in price_str):
            return None
        
        # 移除货币符号和非数字字符（保留小数点和负号）
        # 移除 ¥ $ € £ ฿ ₫ ₩
        price_str = re.sub(r'[^\d\.\-]', '', price_str)
        
        try:
            price = float(price_str)
            # 异常值处理
            if price < 0: return None
            return round(price, 2)
        except ValueError:
            logger.debug(f"价格解析失败：{price_str}")
            return None
    
    @staticmethod
    def _parse_sales(sales_str: Any) -> Optional[int]:
        """
        解析销量字符串
        
        支持格式：
        - "1000"
        - "1000+"
        - "1k"
        - "10w"
        - "3.5万"
        """
        if not sales_str:
            return None
        
        sales_str = str(sales_str).strip().lower()
        
        # 移除加号、件、人付款等后缀
        sales_str = re.sub(r'[+件人付款个已售]', '', sales_str)
        
        try:
            # 处理 k, w, 万
            if sales_str.endswith('k'):
                return int(float(sales_str[:-1]) * 1000)
            elif sales_str.endswith('w') or sales_str.endswith('万'):
                return int(float(sales_str[:-1]) * 10000)
            else:
                return int(float(sales_str))
        except (ValueError, TypeError):
            logger.debug(f"销量解析失败：{sales_str}")
            return None
    
    @staticmethod
    def _parse_rating(rating_str: Any) -> Optional[float]:
        """
        解析评分
        
        支持格式：
        - "4.5"
        - "4.5/5"
        - "4.5星"
        """
        if not rating_str:
            return None
        
        rating_str = str(rating_str).strip()
        
        # 提取数字
        numbers = re.findall(r'\d+\.?\d*', rating_str)
        
        if numbers:
            try:
                rating = float(numbers[0])
                # 范围验证（0-5分制或0-10分制）
                if 0 <= rating <= 5:
                    return round(rating, 1)
                elif 0 <= rating <= 10:
                    return round(rating / 2, 1)
            except ValueError:
                pass
        
        return None
