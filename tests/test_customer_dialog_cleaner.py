# -*- coding: utf-8 -*-
"""
客户对话清洗器单元测试

测试覆盖：
- 对话ID验证
- 消息类型验证
- 文本清洁
- 时间标准化
- 批量清洗
"""

import pytest
from src.cleaner.cleaners.customer_dialog_cleaner import CustomerDialogCleaner


class TestCustomerDialogCleanerInit:
    """清洗器初始化测试"""
    
    def test_cleaner_initialization(self):
        """测试清洗器能正确初始化"""
        cleaner = CustomerDialogCleaner()
        assert cleaner.BUSINESS_TYPE_ID == 'CUSTOMER_DIALOG'
        assert cleaner.PRIMARY_KEY == 'conversation_id'


class TestCustomerDialogRecordCleaning:
    """单记录清洗测试"""
    
    def test_clean_valid_record(self, sample_dialog_record):
        """测试清洗有效对话"""
        cleaner = CustomerDialogCleaner()
        result = cleaner._clean_record(sample_dialog_record)
        
        assert result is not None
        assert result['conversation_id'] == 'CONV_001'
        assert result['is_cleaned'] is True
    
    def test_clean_record_with_missing_conversation_id(self, sample_dialog_record):
        """测试缺少对话ID时返回None"""
        cleaner = CustomerDialogCleaner()
        sample_dialog_record['conversation_id'] = ''
        result = cleaner._clean_record(sample_dialog_record)
        assert result is None
    
    def test_message_type_validation(self, sample_dialog_record):
        """测试消息类型验证"""
        cleaner = CustomerDialogCleaner()
        
        # 有效类型
        sample_dialog_record['message_type'] = 'question'
        result = cleaner._clean_record(sample_dialog_record)
        assert result['message_type'] == 'question'
        
        # 无效类型转为unknown
        sample_dialog_record['message_type'] = 'invalid_type'
        result = cleaner._clean_record(sample_dialog_record)
        assert result['message_type'] == 'unknown'
    
    def test_message_content_cleaning(self, sample_dialog_record):
        """测试消息内容清洁"""
        cleaner = CustomerDialogCleaner()
        
        sample_dialog_record['message_content'] = '请问这个怎么样？😊'
        result = cleaner._clean_record(sample_dialog_record)
        
        assert '😊' not in result['message_content']
        assert '请问' in result['message_content']
    
    def test_customer_and_service_id_handling(self, sample_dialog_record):
        """测试客户和服务人员ID处理"""
        cleaner = CustomerDialogCleaner()
        
        # 缺少客户ID使用UNKNOWN
        sample_dialog_record['customer_id'] = ''
        result = cleaner._clean_record(sample_dialog_record)
        assert result['customer_id'] == 'UNKNOWN'
        
        # 缺少服务人员ID使用SYSTEM
        sample_dialog_record['service_id'] = ''
        result = cleaner._clean_record(sample_dialog_record)
        assert result['service_id'] == 'SYSTEM'


class TestCustomerDialogBatchCleaning:
    """批量清洗测试"""
    
    def test_clean_batch_dialogs(self, sample_dialog_records):
        """测试批量清洗对话 - 超穷样本包含11条"""
        cleaner = CustomerDialogCleaner()
        records, stats = cleaner.clean(sample_dialog_records)
        
        assert stats['original_count'] == 11
        assert stats['success_rate'] >= 0.8
        assert len(records) >= 9
    
    def test_batch_cleaning_statistics(self, sample_dialog_records):
        """测试批量清洗统计信息"""
        cleaner = CustomerDialogCleaner()
        records, stats = cleaner.clean(sample_dialog_records)
        
        assert stats['business_type'] == 'CUSTOMER_DIALOG'
        assert stats['original_count'] == 11
        assert stats['success_rate'] > 0


class TestCustomerDialogValidation:
    """记录验证测试"""
    
    def test_validate_valid_record(self, sample_dialog_record):
        """测试有效记录验证"""
        cleaner = CustomerDialogCleaner()
        assert cleaner.validate_record(sample_dialog_record) is True
    
    def test_validate_record_missing_conversation_id(self, sample_dialog_record):
        """测试缺少对话ID的验证"""
        cleaner = CustomerDialogCleaner()
        sample_dialog_record['conversation_id'] = ''
        assert cleaner.validate_record(sample_dialog_record) is False
