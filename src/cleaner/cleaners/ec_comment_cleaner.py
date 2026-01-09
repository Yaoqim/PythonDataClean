# -*- coding: utf-8 -*-
"""
电商评论清洗器

业务类型：EC_COMMENT
数据表：ec_comment_info

清洗规则（参考《业务类型_2电商商品评论.md》）：

核心字段：
- comment_id：评论ID（主键、必填）
- product_id：商品ID（必填）
- comment_content：评论内容（必填）
- rating_score：评分（1-5）
- comment_date：评论日期（必填）
- comment_level：评论等级（好评/中评/差评）

清洗流程：
1. 验证主键（comment_id） - 缺失则删除记录
2. 验证必填字段 - 缺失则删除记录
3. 评分范围验证（1-5）
4. 评论等级标准化
5. 文本字段清洁（去emoji、去HTML、去URL）
6. 时间字段标准化
7. 可选LLM情感分析
"""

from typing import Dict, Any, Optional
from src.cleaner.base_cleaner import BaseCleaner
from src.utils.logger import get_logger
from src.utils.string_utils import StringUtils
from src.utils.time_utils import TimeUtils
from src.utils.validation import Validator

logger = get_logger(__name__)


class ECCommentCleaner(BaseCleaner):
    """电商评论清洗器"""
    
    # 业务类型标识
    BUSINESS_TYPE_ID = 'EC_COMMENT'
    
    # 主键字段
    PRIMARY_KEY = 'comment_id'
    
    # 必需字段
    REQUIRED_FIELDS = ['comment_id', 'product_id', 'comment_content']
    
    # 核心字段
    CORE_FIELDS = ['comment_id', 'product_id', 'comment_content', 'rating_score', 'comment_date', 'comment_level']
    
    # 评分范围
    RATING_MIN = 1
    RATING_MAX = 5
    
    # 有效评论等级
    VALID_LEVELS = {'好评', '中评', '差评'}
    
    # 评论内容最大长度
    CONTENT_MAX_LENGTH = 5000

    def _clean_record(self, record: Dict[str, Any], llm_client: Any = None) -> Optional[Dict[str, Any]]:
        """
        清洗单条电商评论记录

        Args:
            record: 原始记录
            llm_client: LLM客户端（可选，用于情感分析）

        Returns:
            清洗后的记录，如无法清洗返回None
        """
        if not record:
            return None
        
        # 1. 验证并清洗主键
        comment_id = record.get('comment_id', '').strip()
        if not comment_id:
            logger.debug("评论ID为空，记录被删除")
            return None
        
        cleaned = {'comment_id': comment_id}
        
        # 2. 验证product_id
        product_id = record.get('product_id', '').strip()
        if not product_id:
            logger.debug(f"商品ID为空，评论被删除：{comment_id}")
            return None
        cleaned['product_id'] = product_id
        
        # 3. 验证并清洗评论内容（必填）
        content = record.get('comment_content', '').strip()
        if not content:
            logger.debug(f"评论内容为空，记录被删除：{comment_id}")
            return None
        
        # 文本清洁（去emoji、去HTML、去URL）
        content = StringUtils.clean_text(
            content,
            remove_html=True,
            remove_urls=True,
            remove_emoji=True,
            remove_mentions=False,
            max_length=self.CONTENT_MAX_LENGTH
        )
        
        cleaned['comment_content'] = content
        
        # 4. 清洗评分字段（1-5）
        rating_score = record.get('rating_score')
        if rating_score is not None and rating_score != '':
            try:
                rating_score = int(float(rating_score))
                # 验证范围
                if not Validator.validate_range(rating_score, self.RATING_MIN, self.RATING_MAX, 'rating_score'):
                    logger.debug(f"评分超出范围：{rating_score}，使用NULL")
                    rating_score = None
            except (ValueError, TypeError):
                logger.debug(f"评分转换失败：{rating_score}")
                rating_score = None
        else:
            rating_score = None
        
        cleaned['rating_score'] = rating_score
        
        # 5. 清洗评论等级
        comment_level = record.get('comment_level', '').strip()
        if comment_level not in self.VALID_LEVELS:
            comment_level = '未分类'
        cleaned['comment_level'] = comment_level
        
        # 6. 清洗评论日期（标准化）
        comment_date = record.get('comment_date', '')
        if comment_date:
            try:
                comment_date = TimeUtils.standardize_timestamp(comment_date)
                if not comment_date:
                    comment_date = None
            except Exception as e:
                logger.debug(f"时间转换失败：{record.get('comment_date')}，错误：{e}")
                comment_date = None
        cleaned['comment_date'] = comment_date
        
        # 7. 处理其他可选字段
        user_name = record.get('user_name', '').strip()
        cleaned['user_name'] = user_name or None
        
        # 是否验证购买
        try:
            is_verified = bool(record.get('is_verified', False))
        except (ValueError, TypeError):
            is_verified = False
        cleaned['is_verified'] = is_verified
        
        # 点赞数
        try:
            likes = int(record.get('likes', 0))
            likes = max(0, likes)
        except (ValueError, TypeError):
            likes = 0
        cleaned['likes'] = likes
        
        # 8. 可选LLM情感分析
        if llm_client:
            try:
                sentiment = llm_client.analyze_sentiment(content)
                cleaned['sentiment_label'] = sentiment.get('label')
                cleaned['sentiment_confidence'] = sentiment.get('confidence')
            except Exception as e:
                logger.warning(f"LLM情感分析失败：{e}")
                cleaned['sentiment_label'] = None
                cleaned['sentiment_confidence'] = None
        else:
            cleaned['sentiment_label'] = None
            cleaned['sentiment_confidence'] = None
        
        # 9. 标记清洗状态
        cleaned['is_cleaned'] = True
        cleaned['clean_time'] = None  # 由存储层填充
        
        return cleaned
