# -*- coding: utf-8 -*-
"""
电商商品信息清洗器

业务类型：EC_GOODS_PHONE
数据表：ec_product_info

清洗规则（参考《业务类型_1电商平台数据.md》）：

核心字段：
- product_id：商品ID（主键、必填）
- title：商品名称（必填）
- price：价格（必填、数值）
- currency_code：货币代码（必填）
- shop_name：店铺名称（必填）
- source_platform：数据来源平台（必填）

清洗流程：
1. 验证主键（product_id）- 缺失则删除记录
2. 验证必填字段 - 缺失则删除记录
3. 文本字段标准化（title、shop_name等）
4. 数值字段转换（price转为float）
5. 时间字段标准化（如果存在）
"""

from typing import Dict, Any, Optional, List
from src.cleaner.base_cleaner import BaseCleaner
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.validation import Validator

logger = get_logger(__name__)


class ECGoodsCleaner(BaseCleaner):
    """电商商品清洗器"""
    
    # 业务类型标识
    BUSINESS_TYPE_ID = 'EC_GOODS_PHONE'
    
    # 主键字段
    PRIMARY_KEY = 'product_id'
    
    # 必需字段
    REQUIRED_FIELDS = ['product_id', 'title']
    
    # 核心字段（需要进行准确度评估）
    CORE_FIELDS = ['product_id', 'title', 'price', 'currency_code', 'shop_name', 'source_platform']
    
    # 价格范围验证
    PRICE_MIN = 0
    PRICE_MAX = 999999
    
    # 商品名称最大长度
    TITLE_MAX_LENGTH = 500
    
    # 店铺名称最大长度
    SHOP_NAME_MAX_LENGTH = 200
    
    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条电商商品记录
        
        Args:
            record: 原始记录
            llm_client: LLM客户端（可选）
        
        Returns:
            清洗后的记录，如无法清洗返回None
        """
        if not record:
            return None
        
        # 1. 验证并清洗主键
        product_id = record.get('product_id', '').strip()
        if not product_id:
            logger.debug("商品ID为空，记录被删除")
            return None
        
        cleaned = {'product_id': product_id}
        
        # 2. 验证并清洗商品名称（必填、文本）
        title = record.get('title', '').strip()
        if not title:
            logger.debug(f"商品名称为空，记录被删除：{product_id}")
            return None
        
        # 文本清洁
        title = StringUtils.clean_text(
            title,
            remove_html=True,
            remove_urls=True,
            remove_emoji=True,
            remove_mentions=False,
            max_length=self.TITLE_MAX_LENGTH
        )
        
        cleaned['title'] = title
        
        # 3. 清洗价格字段（必填、数值）
        price_raw = record.get('price')
        price = None
        
        if price_raw is not None and price_raw != '':
            try:
                # 移除特殊字符（¥、$、逗号等）
                price_str = str(price_raw).replace('¥', '').replace('$', '').replace(',', '').strip()
                price = float(price_str)
                
                # 验证价格范围
                if not Validator.validate_range(price, self.PRICE_MIN, self.PRICE_MAX, 'price'):
                    logger.debug(f"价格超出范围：{price}，使用NULL")
                    price = None
                else:
                    price = round(price, 2)
            except (ValueError, TypeError) as e:
                logger.debug(f"价格转换失败：{price_raw}，错误：{e}")
                price = None
        
        cleaned['price'] = price
        
        # 4. 清洗货币代码
        currency_code = record.get('currency_code', 'CNY').strip().upper()
        # 验证货币代码格式（3字符字母）
        if not currency_code or len(currency_code) != 3 or not currency_code.isalpha():
            currency_code = 'CNY'
        cleaned['currency_code'] = currency_code
        
        # 5. 清洗店铺名称
        shop_name = record.get('shop_name', '').strip()
        if shop_name:
            shop_name = StringUtils.remove_special_chars(shop_name, keep_punctuation=True)
            if len(shop_name) > self.SHOP_NAME_MAX_LENGTH:
                shop_name = shop_name[:self.SHOP_NAME_MAX_LENGTH]
        cleaned['shop_name'] = shop_name or '未知'
        
        # 6. 清洗数据来源平台
        source_platform = record.get('source_platform', '').strip()
        if not source_platform:
            source_platform = '未知'
        cleaned['source_platform'] = source_platform
        
        # 7. 处理其他可选字段
        # 品牌
        brand = record.get('brand', '').strip()
        if brand:
            brand = StringUtils.remove_special_chars(brand, keep_punctuation=False)
        cleaned['brand'] = brand or None
        
        # 分类
        category = record.get('category', '').strip()
        cleaned['category'] = category or None
        
        # 销量
        try:
            sales = int(record.get('sales', 0))
            sales = max(0, sales)
        except (ValueError, TypeError):
            sales = 0
        cleaned['sales'] = sales
        
        # 评分
        try:
            rating = float(record.get('rating', 0))
            rating = max(0, min(5, rating))  # 限制在0-5
            rating = round(rating, 2)
        except (ValueError, TypeError):
            rating = 0.0
        cleaned['rating'] = rating
        
        # 8. 标记清洗状态
        cleaned['is_cleaned'] = True
        cleaned['clean_time'] = None  # 由存储层填充
        
        return cleaned
