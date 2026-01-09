# -*- coding: utf-8 -*-
"""
pytest 配置和共享 fixtures

提供测试数据和公共 fixture
"""

import pytest
import sys
from pathlib import Path

# 添加项目根路径
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture
def sample_goods_record():
    """电商商品样本记录 - 标准记录"""
    return {
        'product_id': 'PROD_001',
        'title': '【正品】iPhone 15 Pro Max 手机 256GB',
        'price': '¥8999',
        'currency_code': 'CNY',
        'shop_name': '官方旗舰店',
        'source_platform': 'JD',
        'brand': '苹果',
        'original_price': '10999',
        'spec_params': '{"processor": "A17 Pro", "ram": "8GB"}',
        'sales_volume': 15000,
        'comment_count': 5200,
        'rating': 4.8,
        'good_rate': 95.5,
        'shop_id': 'SHOP_001',
        'is_official': 1,
        'listing_time': '2024-01-01 10:00:00',
        'update_time': '2024-01-08 15:30:00'
    }


@pytest.fixture
def sample_goods_records():
    """电商商品样本记录列表 - 涵盖各种清洗场景"""
    return [
        # 场景1: 标准记录
        {
            'product_id': 'PROD_001',
            'title': 'Apple iPhone 15 Pro Max',
            'price': '8999',
            'currency_code': 'CNY',
            'shop_name': '官方店',
            'source_platform': 'JD',
            'original_price': '10999',
            'brand': 'Apple',
            'rating': 4.8,
            'good_rate': 95.5,
            'sales_volume': 15000,
            'comment_count': 5200,
            'is_official': 1,
            'listing_time': '2024-01-01 10:00:00',
            'update_time': '2024-01-08 15:30:00'
        },
        # 场景2: 美元价格（多币种）
        {
            'product_id': 'PROD_002',
            'title': 'Samsung Galaxy S24 Ultra',
            'price': '$999.99',
            'currency_code': 'USD',
            'shop_name': 'Amazon',
            'source_platform': 'Amazon',
            'rating': 4.5,
            'good_rate': 92.0,
            'sales_volume': 8500
        },
        # 场景3: 欧元价格
        {
            'product_id': 'PROD_003',
            'title': 'MacBook Pro 16英寸 M3 Max',
            'price': '€1899',
            'currency_code': 'EUR',
            'shop_name': 'Apple Store',
            'source_platform': 'JD',
            'brand': 'Apple',
            'rating': 4.9,
            'original_price': '€2099'
        },
        # 场景4: 标题含平台标记
        {
            'product_id': 'PROD_004',
            'title': '【官方旗舰店】小米 14 Pro 新款手机',
            'price': '3999',
            'currency_code': 'CNY',
            'shop_name': '小米官方',
            'source_platform': 'Taobao',
            'is_official': 0
        },
        # 场景5: 标题含特殊字符和emoji
        {
            'product_id': 'PROD_005',
            'title': 'iPad Pro 12.9" ✨ 最新款 🎉 性价比之选',
            'price': '5999',
            'currency_code': 'CNY',
            'shop_name': 'Apple专卖店',
            'source_platform': 'JD'
        },
        # 场景6: 标题超长（测试截断）
        {
            'product_id': 'PROD_006',
            'title': '华为Mate 60 Pro Plus 5G旗舰智能手机最新款高端商务办公学生全网通支持NFC支付无损音乐播放摄影功能强大电池续航长' + 'x' * 200,
            'price': '4999',
            'currency_code': 'CNY',
            'shop_name': '华为官方',
            'source_platform': 'Taobao'
        },
        # 场景7: 销量含单位（需要转换）
        {
            'product_id': 'PROD_007',
            'title': 'AirPods Pro 第二代',
            'price': '1899',
            'currency_code': 'CNY',
            'shop_name': 'Apple',
            'source_platform': 'JD',
            'sales_volume': '3.5万件'
        },
        # 场景8: 评分异常值（超出0-5范围）
        {
            'product_id': 'PROD_008',
            'title': 'Google Pixel 8',
            'price': '6299',
            'currency_code': 'CNY',
            'shop_name': 'Google',
            'source_platform': 'JD',
            'rating': 9.5  # 异常值
        },
        # 场景9: 缺少product_id
        {
            'product_id': '',
            'title': 'OnePlus 12',
            'price': '4599',
            'currency_code': 'CNY',
            'shop_name': 'OnePlus',
            'source_platform': 'JD'
        },
        # 场景10: 缺少title
        {
            'product_id': 'PROD_010',
            'title': '',
            'price': '3299',
            'currency_code': 'CNY',
            'shop_name': 'Xiaomi',
            'source_platform': 'JD'
        },
        # 场景11: 缺少price
        {
            'product_id': 'PROD_011',
            'title': 'vivo X100',
            'price': None,
            'currency_code': 'CNY',
            'shop_name': 'vivo',
            'source_platform': 'JD'
        },
        # 场景12: 价格为负数（异常）
        {
            'product_id': 'PROD_012',
            'title': 'OPPO Find X7',
            'price': '-999',
            'currency_code': 'CNY',
            'shop_name': 'OPPO',
            'source_platform': 'JD'
        },
        # 场景13: 价格超出范围
        {
            'product_id': 'PROD_013',
            'title': '高端商务笔记本',
            'price': '9999999',
            'currency_code': 'CNY',
            'shop_name': 'Dell',
            'source_platform': 'JD'
        },
        # 场景14: 货币代码无效
        {
            'product_id': 'PROD_014',
            'title': 'Sony WH-1000XM5',
            'price': '2399',
            'currency_code': 'INVALID',
            'shop_name': 'Sony',
            'source_platform': 'JD'
        },
        # 场景15: 缺少shop_name（应填充"未知"）
        {
            'product_id': 'PROD_015',
            'title': 'JBL Flip 6',
            'price': '599',
            'currency_code': 'CNY',
            'shop_name': '',
            'source_platform': 'JD'
        },
        # 场景16: 好评率异常（>100%）
        {
            'product_id': 'PROD_016',
            'title': 'Beats Studio Pro',
            'price': '2999',
            'currency_code': 'CNY',
            'shop_name': 'Beats',
            'source_platform': 'JD',
            'good_rate': 120  # 异常
        },
        # 场景17: 规格参数JSON格式
        {
            'product_id': 'PROD_017',
            'title': 'ASUS VivoBook',
            'price': '4999',
            'currency_code': 'CNY',
            'shop_name': 'ASUS',
            'source_platform': 'JD',
            'spec_params': '{"processor": "AMD Ryzen 7", "ram": "16GB", "storage": "512GB SSD"}'
        },
        # 场景18: 时间格式化
        {
            'product_id': 'PROD_018',
            'title': 'Lenovo ThinkPad',
            'price': '5999',
            'currency_code': 'CNY',
            'shop_name': 'Lenovo',
            'source_platform': 'JD',
            'listing_time': '2024-01-01',  # 需要格式化
            'update_time': '3天前'  # 相对时间，需要转换
        },
        # 场景19: 重复记录（相同product_id）
        {
            'product_id': 'PROD_001',
            'title': 'Apple iPhone 15 Pro Max',
            'price': '8999',
            'currency_code': 'CNY',
            'shop_name': '官方店',
            'source_platform': 'JD',
            'rating': 4.8,
            'update_time': '2024-01-09 10:00:00'  # 更新时间较新
        }
    ]


@pytest.fixture
def sample_comment_record():
    """电商评論样本记录 - 标准记录"""
    return {
        'comment_id': 'CMT_001',
        'product_id': 'PROD_001',
        'user_name': '用户A',
        'comment_content': '不错的选择，一上手就喜欢了！',
        'rating_score': 5,
        'comment_date': '2024-01-08',
        'comment_level': '好评',
        'is_verified': 1,
        'likes': 100
    }


@pytest.fixture
def sample_comment_records():
    """电商评論样本记录列表 - 涵盖各种场景"""
    return [
        # 场景1: 标准好评
        {
            'comment_id': 'CMT_001',
            'product_id': 'PROD_001',
            'user_name': '用户A',
            'comment_content': '不错的选择，官方店一上手就喜欢！',
            'rating_score': 5,
            'comment_date': '2024-01-08',
            'comment_level': '好评',
            'is_verified': 1,
            'likes': 100
        },
        # 场景2: 中评
        {
            'comment_id': 'CMT_002',
            'product_id': 'PROD_001',
            'user_name': '用户B',
            'comment_content': '性能不错，电池续航一般',
            'rating_score': 3,
            'comment_date': '2024-01-07',
            'comment_level': '中评',
            'is_verified': 0,
            'likes': 10
        },
        # 场景3: 低评
        {
            'comment_id': 'CMT_003',
            'product_id': 'PROD_002',
            'user_name': '用户C',
            'comment_content': '质量不好，一个月就卡顿了！',
            'rating_score': 1,
            'comment_date': '2024-01-06',
            'comment_level': '差评',
            'is_verified': 1,
            'likes': 0
        },
        # 场景4: 作粗评分超出范围(>5)
        {
            'comment_id': 'CMT_004',
            'product_id': 'PROD_001',
            'user_name': '用户D',
            'comment_content': '太棒了！！！',
            'rating_score': 10,  # 异常
            'comment_date': '2024-01-08',
            'comment_level': '好评',
            'is_verified': 1,
            'likes': 50
        },
        # 场景5: 评分超出下限(0)
        {
            'comment_id': 'CMT_005',
            'product_id': 'PROD_001',
            'user_name': '用户E',
            'comment_content': '极其失望',
            'rating_score': -1,  # 异常
            'comment_date': '2024-01-08',
            'comment_level': '差评',
            'is_verified': 0,
            'likes': 2
        },
        # 场景6: 评論内容含HTML和emoji
        {
            'comment_id': 'CMT_006',
            'product_id': 'PROD_001',
            'user_name': '用户F',
            'comment_content': '太棒了<br>大妹们不同an😋 http://example.com',
            'rating_score': 5,
            'comment_date': '2024-01-08',
            'comment_level': '好评',
            'is_verified': 1,
            'likes': 150
        },
        # 场景7: 缺少comment_id
        {
            'comment_id': '',
            'product_id': 'PROD_001',
            'user_name': '用户G',
            'comment_content': '这是一条需要删除的评論',
            'rating_score': 3,
            'comment_date': '2024-01-08',
            'comment_level': '中评',
            'is_verified': 0,
            'likes': 0
        },
        # 场景8: 缺少评論内容
        {
            'comment_id': 'CMT_008',
            'product_id': 'PROD_001',
            'user_name': '用户H',
            'comment_content': '',  # 缺少
            'rating_score': 3,
            'comment_date': '2024-01-08',
            'comment_level': '中评',
            'is_verified': 0,
            'likes': 0
        },
        # 场景9: 缺少product_id
        {
            'comment_id': 'CMT_009',
            'product_id': '',
            'user_name': '用户I',
            'comment_content': '有些不错',
            'rating_score': 4,
            'comment_date': '2024-01-08',
            'comment_level': '好评',
            'is_verified': 1,
            'likes': 20
        },
        # 场景10: 无效的评論等级
        {
            'comment_id': 'CMT_010',
            'product_id': 'PROD_001',
            'user_name': '用户J',
            'comment_content': '这是一条无效评論',
            'rating_score': 2,
            'comment_date': '2024-01-08',
            'comment_level': '未分类',  # 异常
            'is_verified': 0,
            'likes': 0
        }
    ]


@pytest.fixture
def sample_dialog_record():
    """客户对话样本记录 - 标准记录"""
    return {
        'conversation_id': 'CONV_001',
        'customer_id': 'CUST_001',
        'service_id': 'SRV_001',
        'message_content': '请问这个商品怎么样？有什么优惠吗？',
        'message_time': '2024-01-08 10:30:00',
        'message_type': 'question',
        'duration_seconds': 300,
        'satisfaction_score': 4,
        'is_resolved': 1
    }


@pytest.fixture
def sample_dialog_records():
    """客户对话样本记录列表 - 涵盖各种场景"""
    return [
        # 场景1: 标准问答类对话
        {
            'conversation_id': 'CONV_001',
            'customer_id': 'CUST_001',
            'service_id': 'SRV_001',
            'message_content': '请问有现货吗？有续什么时候有？',
            'message_time': '2024-01-08 10:30:00',
            'message_type': 'question',
            'duration_seconds': 300,
            'satisfaction_score': 5,
            'is_resolved': 1
        },
        # 场景2: 反映类对话（投诉）
        {
            'conversation_id': 'CONV_002',
            'customer_id': 'CUST_002',
            'service_id': 'SRV_002',
            'message_content': '我要投评这个产品！缺陷太多！',
            'message_time': '2024-01-08 11:00:00',
            'message_type': 'feedback',
            'duration_seconds': 600,
            'satisfaction_score': 1,
            'is_resolved': 0
        },
        # 场景3: 关闭type
        {
            'conversation_id': 'CONV_003',
            'customer_id': 'CUST_003',
            'service_id': 'SRV_001',
            'message_content': '多谢你的帮助！',
            'message_time': '2024-01-08 12:00:00',
            'message_type': 'closing',
            'duration_seconds': 120,
            'satisfaction_score': 5,
            'is_resolved': 1
        },
        # 场景4: 缺少customer_id（应填充UNKNOWN）
        {
            'conversation_id': 'CONV_004',
            'customer_id': '',
            'service_id': 'SRV_001',
            'message_content': '请问需要多久向发？',
            'message_time': '2024-01-08 13:00:00',
            'message_type': 'question',
            'duration_seconds': 180,
            'satisfaction_score': 3,
            'is_resolved': 1
        },
        # 场景5: 缺少service_id（应填充SYSTEM）
        {
            'conversation_id': 'CONV_005',
            'customer_id': 'CUST_005',
            'service_id': '',
            'message_content': '使用方法是什么？',
            'message_time': '2024-01-08 14:00:00',
            'message_type': 'question',
            'duration_seconds': 240,
            'satisfaction_score': 4,
            'is_resolved': 1
        },
        # 场景6: 消息内容含emoji
        {
            'conversation_id': 'CONV_006',
            'customer_id': 'CUST_006',
            'service_id': 'SRV_002',
            'message_content': '太棒了😋 这个产品真的很不错！',
            'message_time': '2024-01-08 15:00:00',
            'message_type': 'feedback',
            'duration_seconds': 150,
            'satisfaction_score': 5,
            'is_resolved': 1
        },
        # 场景7: 缺少conversation_id
        {
            'conversation_id': '',
            'customer_id': 'CUST_007',
            'service_id': 'SRV_001',
            'message_content': '这条应该被删除',
            'message_time': '2024-01-08 16:00:00',
            'message_type': 'question',
            'duration_seconds': 100,
            'satisfaction_score': 2,
            'is_resolved': 0
        },
        # 场景8: 缺少message_content
        {
            'conversation_id': 'CONV_008',
            'customer_id': 'CUST_008',
            'service_id': 'SRV_001',
            'message_content': '',  # 缺少
            'message_time': '2024-01-08 17:00:00',
            'message_type': 'question',
            'duration_seconds': 50,
            'satisfaction_score': 3,
            'is_resolved': 0
        },
        # 场景9: 恒升筢算类型（无效的message_type）
        {
            'conversation_id': 'CONV_009',
            'customer_id': 'CUST_009',
            'service_id': 'SRV_001',
            'message_content': '这是一条帮助',
            'message_time': '2024-01-08 18:00:00',
            'message_type': 'invalid_type',  # 异常
            'duration_seconds': 200,
            'satisfaction_score': 3,
            'is_resolved': 1
        },
        # 场景10: 满意度超出范围(>5)
        {
            'conversation_id': 'CONV_010',
            'customer_id': 'CUST_010',
            'service_id': 'SRV_001',
            'message_content': '服务状态特或坏！',
            'message_time': '2024-01-08 19:00:00',
            'message_type': 'feedback',
            'duration_seconds': 300,
            'satisfaction_score': 10,  # 异常
            'is_resolved': 0
        },
        # 场景11: 满意度下限(<0)
        {
            'conversation_id': 'CONV_011',
            'customer_id': 'CUST_011',
            'service_id': 'SRV_001',
            'message_content': '极其失望',
            'message_time': '2024-01-08 20:00:00',
            'message_type': 'feedback',
            'duration_seconds': 450,
            'satisfaction_score': -5,  # 异常
            'is_resolved': 0
        }
    ]
