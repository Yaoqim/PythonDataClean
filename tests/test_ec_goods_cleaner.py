# -*- coding: utf-8 -*-
"""
电商商品清洗器单元测试

测试覆盖：
- 主键验证
- 必填字段验证
- 文本清洁
- 数值转换
- 范围验证
- 批量清洗
"""

import pytest
from src.cleaner.cleaners.ec_goods_cleaner import ECGoodsCleaner


class TestECGoodsCleanerInit:
    """清洗器初始化测试"""
    
    def test_cleaner_initialization(self):
        """测试清洗器能正确初始化"""
        cleaner = ECGoodsCleaner()
        assert cleaner.BUSINESS_TYPE_ID == 'EC_GOODS_PHONE'
        assert cleaner.PRIMARY_KEY == 'product_id'
        assert len(cleaner.REQUIRED_FIELDS) > 0


class TestECGoodsRecordCleaning:
    """单记录清洗测试"""
    
    def test_clean_valid_record(self, sample_goods_record):
        """测试清洗有效记录"""
        cleaner = ECGoodsCleaner()
        result = cleaner._clean_record(sample_goods_record)
        
        assert result is not None
        assert result['product_id'] == 'PROD_001'
        assert result['is_cleaned'] is True
        assert 'title' in result
    
    def test_clean_record_with_missing_product_id(self, sample_goods_record):
        """测试缺少product_id时返回None"""
        cleaner = ECGoodsCleaner()
        sample_goods_record['product_id'] = ''
        result = cleaner._clean_record(sample_goods_record)
        assert result is None
    
    def test_clean_record_with_missing_title(self, sample_goods_record):
        """测试缺少title时返回None"""
        cleaner = ECGoodsCleaner()
        sample_goods_record['title'] = ''
        result = cleaner._clean_record(sample_goods_record)
        assert result is None
    
    def test_price_conversion(self, sample_goods_record):
        """测试价格转换"""
        cleaner = ECGoodsCleaner()
        
        # 测试带符号的价格
        sample_goods_record['price'] = '¥8999'
        result = cleaner._clean_record(sample_goods_record)
        assert result['price'] == 8999.0
        
        # 测试普通数字
        sample_goods_record['price'] = '1999.99'
        result = cleaner._clean_record(sample_goods_record)
        assert result['price'] == 1999.99
    
    def test_price_range_validation(self, sample_goods_record):
        """测试价格范围验证"""
        cleaner = ECGoodsCleaner()
        
        # 超出范围
        sample_goods_record['price'] = '1000000'
        result = cleaner._clean_record(sample_goods_record)
        assert result['price'] is None
        
        # 负数
        sample_goods_record['price'] = '-100'
        result = cleaner._clean_record(sample_goods_record)
        assert result['price'] is None
    
    def test_currency_code_normalization(self, sample_goods_record):
        """测试货币代码标准化"""
        cleaner = ECGoodsCleaner()
        
        # 小写转大写
        sample_goods_record['currency_code'] = 'cny'
        result = cleaner._clean_record(sample_goods_record)
        assert result['currency_code'] == 'CNY'
        
        # 无效货币代码转为默认值
        sample_goods_record['currency_code'] = 'INVALID'
        result = cleaner._clean_record(sample_goods_record)
        assert result['currency_code'] == 'CNY'
    
    def test_rating_validation(self, sample_goods_record):
        """测试评分范围限制"""
        cleaner = ECGoodsCleaner()
        
        # 超过5.0
        sample_goods_record['rating'] = 10.0
        result = cleaner._clean_record(sample_goods_record)
        assert result['rating'] == 5.0
        
        # 负数
        sample_goods_record['rating'] = -1.0
        result = cleaner._clean_record(sample_goods_record)
        assert result['rating'] == 0.0


class TestECGoodsBatchCleaning:
    """批量清洗测试"""
    
    def test_clean_batch_records(self, sample_goods_records):
        """测试批量清洗"""
        cleaner = ECGoodsCleaner()
        records, stats = cleaner.clean(sample_goods_records)
        
        # 超穷样本包含尚慠场景，检查成功率
        assert stats['original_count'] == 19
        assert stats['success_rate'] >= 0.8
        assert len(records) >= 15
    
    def test_batch_cleaning_with_empty_list(self):
        """测试空列表清洗"""
        cleaner = ECGoodsCleaner()
        records, stats = cleaner.clean([])
        
        assert len(records) == 0
        assert stats['cleaned_count'] == 0
    
    def test_batch_cleaning_statistics(self, sample_goods_records):
        """测试批量清洗统计信息"""
        cleaner = ECGoodsCleaner()
        records, stats = cleaner.clean(sample_goods_records)
        
        assert stats['business_type'] == 'EC_GOODS_PHONE'
        assert stats['original_count'] == 19  # 壳穷样本总数
        assert stats['success_rate'] > 0


class TestECGoodsTextCleaning:
    """文本清洁测试"""
    
    def test_title_cleaning(self, sample_goods_record):
        """测试商品名称清洁"""
        cleaner = ECGoodsCleaner()
        
        # HTML标签、emoji等
        sample_goods_record['title'] = '苹果iPhone 15 🎉 <b>最新款</b>'
        result = cleaner._clean_record(sample_goods_record)
        
        assert 'iPhone' in result['title']
        assert '🎉' not in result['title']
        assert '<b>' not in result['title']
    
    def test_shop_name_cleaning(self, sample_goods_record):
        """测试店铺名称清洁"""
        cleaner = ECGoodsCleaner()
        
        sample_goods_record['shop_name'] = '官方旗舰店@@@'
        result = cleaner._clean_record(sample_goods_record)
        
        assert '@' not in result['shop_name']
        assert '官方旗舰店' in result['shop_name']


class TestECGoodsValidation:
    """记录验证测试"""
    
    def test_validate_valid_record(self, sample_goods_record):
        """测试有效记录验证"""
        cleaner = ECGoodsCleaner()
        assert cleaner.validate_record(sample_goods_record) is True
    
    def test_validate_record_missing_primary_key(self, sample_goods_record):
        """测试缺少主键的验证"""
        cleaner = ECGoodsCleaner()
        sample_goods_record['product_id'] = ''
        assert cleaner.validate_record(sample_goods_record) is False
    
    def test_validate_record_missing_required_field(self, sample_goods_record):
        """测试缺少必填字段的验证"""
        cleaner = ECGoodsCleaner()
        sample_goods_record['title'] = None
        assert cleaner.validate_record(sample_goods_record) is False
