# -*- coding: utf-8 -*-
"""
电商评论清洗器单元测试

测试覆盖：
- 评论ID验证
- 评分范围验证
- 文本清洁
- 时间标准化
- 批量清洗
"""

import pytest
from src.cleaner.cleaners.ec_comment_cleaner import ECCommentCleaner


class TestECCommentCleanerInit:
    """清洗器初始化测试"""
    
    def test_cleaner_initialization(self):
        """测试清洗器能正确初始化"""
        cleaner = ECCommentCleaner()
        assert cleaner.BUSINESS_TYPE_ID == 'EC_COMMENT'
        assert cleaner.PRIMARY_KEY == 'comment_id'


class TestECCommentRecordCleaning:
    """单记录清洗测试"""
    
    def test_clean_valid_record(self, sample_comment_record):
        """测试清洗有效评论"""
        cleaner = ECCommentCleaner()
        result = cleaner._clean_record(sample_comment_record)
        
        assert result is not None
        assert result['comment_id'] == 'CMT_001'
        assert result['is_cleaned'] is True
    
    def test_clean_record_with_missing_comment_id(self, sample_comment_record):
        """测试缺少comment_id时返回None"""
        cleaner = ECCommentCleaner()
        sample_comment_record['comment_id'] = ''
        result = cleaner._clean_record(sample_comment_record)
        assert result is None
    
    def test_rating_score_validation(self, sample_comment_record):
        """测试评分范围验证"""
        cleaner = ECCommentCleaner()
        
        # 有效评分
        sample_comment_record['rating_score'] = '4'
        result = cleaner._clean_record(sample_comment_record)
        assert result['rating_score'] == 4
        
        # 超出范围
        sample_comment_record['rating_score'] = '10'
        result = cleaner._clean_record(sample_comment_record)
        assert result['rating_score'] is None
    
    def test_comment_content_cleaning(self, sample_comment_record):
        """测试评论内容清洁"""
        cleaner = ECCommentCleaner()
        
        sample_comment_record['comment_content'] = '很好用！<br>推荐购买🎉 http://example.com'
        result = cleaner._clean_record(sample_comment_record)
        
        assert '<br>' not in result['comment_content']
        assert '🎉' not in result['comment_content']
        assert 'http' not in result['comment_content']
        assert '很好用' in result['comment_content']


class TestECCommentBatchCleaning:
    """批量清洗测试"""
    
    def test_clean_batch_comments(self, sample_comment_records):
        """测试批量清洗评论 - 超穷样本包含10条"""
        cleaner = ECCommentCleaner()
        records, stats = cleaner.clean(sample_comment_records)
        
        assert stats['original_count'] == 10
        assert stats['success_rate'] >= 0.7
        assert len(records) >= 7
    
    def test_batch_cleaning_statistics(self, sample_comment_records):
        """测试批量清洗统计信息"""
        cleaner = ECCommentCleaner()
        records, stats = cleaner.clean(sample_comment_records)
        
        assert stats['business_type'] == 'EC_COMMENT'
        assert stats['original_count'] == 10
        assert stats['success_rate'] > 0


class TestECCommentValidation:
    """记录验证测试"""
    
    def test_validate_valid_record(self, sample_comment_record):
        """测试有效记录验证"""
        cleaner = ECCommentCleaner()
        assert cleaner.validate_record(sample_comment_record) is True
    
    def test_validate_record_missing_comment_id(self, sample_comment_record):
        """测试缺少comment_id的验证"""
        cleaner = ECCommentCleaner()
        sample_comment_record['comment_id'] = ''
        assert cleaner.validate_record(sample_comment_record) is False
