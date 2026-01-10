# -*- coding: utf-8 -*-
"""
电商商品数据清洗器

业务类型_1：EC_GOODS_PHONE
清洗规则：商品字段标准化、价格数值化、销量有效性验证
"""

from typing import List, Dict, Any, Optional
import re

from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.validation import Validator
from src.utils.statistics import Statistics

logger = get_logger(__name__)


class ECGoodsPhoneCleaner:
    """
    电商商品清洗器
    
    清洗目标：
    1. 商品名称去重、去HTML、截断
    2. 价格转换为浮点数、范围验证
    3. 销量有效性检查
    4. 分类标准化
    """
    
    # 配置
    MAX_PRODUCT_NAME_LEN = 200
    MIN_PRICE = 0.01
    MAX_PRICE = 10000000
    MAX_SALES = 99999999
    
    @staticmethod
    def clean(records: List[Dict[str, Any]], enable_llm: bool = False) -> Dict[str, Any]:
        """
        清洗电商商品数据
        
        Args:
            records: 原始记录列表
            enable_llm: 是否启用LLM辅助清洗（可选）
        
        Returns:
            清洗结果字典
        """
        logger.info(f"开始清洗电商商品数据，记录数：{len(records)}，LLM启用：{enable_llm}")
        
        cleaned_records = []
        errors = []
        
        for idx, record in enumerate(records):
            try:
                cleaned_record = ECGoodsPhoneCleaner._clean_record(record)
                if cleaned_record:
                    cleaned_records.append(cleaned_record)
            except Exception as e:
                errors.append(f"第{idx+1}行清洗失败：{e}")
                logger.warning(f"记录清洗失败：{e}")
        
        # 计算统计信息
        dedup_rate = Statistics.calculate_dedup_rate(cleaned_records, 'product_id')
        missing_rate = Statistics.calculate_missing_rate(cleaned_records)
        
        logger.info(f"电商商品清洗完成：{len(cleaned_records)}/{len(records)}，去重率：{dedup_rate:.2%}")
        
        return {
            'success': True,
            'business_type_id': 'EC_GOODS_PHONE',
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
    def _clean_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        清洗单条记录
        
        Args:
            record: 原始记录
        
        Returns:
            清洗后的记录（字段名与ec_product_info表一致）
        """
        from datetime import datetime, date
        
        cleaned = {}
        
        # 商品ID（去重依据，必填）
        product_id = record.get('product_id', '').strip()
        if not product_id:
            logger.warning("缺少product_id，跳过记录")
            return None
        cleaned['product_id'] = product_id
        
        # 商品标题（映射到 title）
        title = record.get('product_name', '') or record.get('title', '')
        title = title.strip()
        if title:
            title = StringUtils.clean_text(title)
            title = StringUtils.truncate_text(title, 200)  # 数据库title字段最大200字符
        else:
            # title 是必填字段
            logger.warning(f"缺少title字段：{product_id}")
            return None
        cleaned['title'] = title
        
        # 价格（数值化，必填）
        price_str = record.get('price', '')
        price = ECGoodsPhoneCleaner._parse_price(price_str)
        if price is None:
            logger.warning(f"无效的价格：{price_str}")
            return None  # price 是必填字段
        # 范围验证
        if not Validator.validate_range(price, ECGoodsPhoneCleaner.MIN_PRICE, ECGoodsPhoneCleaner.MAX_PRICE):
            logger.warning(f"价格超出范围：{price}")
            return None
        cleaned['price'] = price
        
        # 货币代码
        currency_code = record.get('currency_code', 'CNY').strip().upper()
        if not currency_code or len(currency_code) != 3 or not currency_code.isalpha():
            currency_code = 'CNY'
        cleaned['currency_code'] = currency_code
        
        # 店铺名称
        shop_name = record.get('shop_name', '').strip()
        if shop_name:
            shop_name = StringUtils.remove_special_chars(shop_name, keep_punctuation=True)
            if len(shop_name) > 100:  # 数据库shop_name字段最大100字符
                shop_name = shop_name[:100]
        cleaned['shop_name'] = shop_name or '未知'
        
        # 来源平台（必填）
        source_platform = record.get('source_platform', '').strip()
        if not source_platform:
            source_platform = record.get('platform', '').strip()
        if not source_platform:
            source_platform = '未知'
        cleaned['source_platform'] = source_platform
        
        # 品牌
        brand = record.get('brand', '').strip()
        if brand:
            brand = StringUtils.remove_special_chars(brand, keep_punctuation=False)
        cleaned['brand'] = brand or None
        
        # 分类
        category = record.get('category', '').strip()
        if category:
            category = StringUtils.clean_text(category)
        cleaned['category'] = category or None
        
        # 销量（映射到 sales_volume）
        sales_str = record.get('sales', '')
        sales_volume = ECGoodsPhoneCleaner._parse_sales(sales_str)
        if sales_volume is not None and (sales_volume < 0 or sales_volume > ECGoodsPhoneCleaner.MAX_SALES):
            sales_volume = None
        cleaned['sales_volume'] = sales_volume or 0
        
        # 评分
        rating_str = record.get('rating', '')
        rating = ECGoodsPhoneCleaner._parse_rating(rating_str)
        cleaned['rating'] = rating or 0.0
        
        # 数据抓取日期（必填）
        data_crawl_date = record.get('data_crawl_date')
        if isinstance(data_crawl_date, str):
            try:
                data_crawl_date = datetime.strptime(data_crawl_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                data_crawl_date = date.today()
        elif isinstance(data_crawl_date, datetime):
            data_crawl_date = data_crawl_date.date()
        elif not isinstance(data_crawl_date, date):
            data_crawl_date = date.today()
        cleaned['data_crawl_date'] = data_crawl_date
        
        # 标记为已清洗
        cleaned['is_cleaned'] = 1
        
        return cleaned
    
    @staticmethod
    def _parse_price(price_str: Any) -> Optional[float]:
        """
        解析价格字符串
        
        支持格式：
        - "99.99"
        - "99"
        - "¥99.99"
        - "$99.99"
        """
        if not price_str:
            return None
        
        price_str = str(price_str).strip()
        
        # 移除货币符号
        price_str = re.sub(r'[¥$€]', '', price_str)
        
        # 移除逗号
        price_str = re.sub(r',', '', price_str)
        
        try:
            price = float(price_str)
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
        """
        if not sales_str:
            return None
        
        sales_str = str(sales_str).strip().lower()
        
        # 移除加号
        sales_str = sales_str.rstrip('+')
        
        try:
            # 处理 k 和 w
            if sales_str.endswith('k'):
                return int(float(sales_str[:-1]) * 1000)
            elif sales_str.endswith('w'):
                return int(float(sales_str[:-1]) * 10000)
            else:
                return int(sales_str)
        except ValueError:
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
