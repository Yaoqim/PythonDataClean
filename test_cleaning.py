# -*- coding: utf-8 -*-
"""
测试脚本

测试3个业务类型的清洗功能
"""

import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_service import MCPDataCleaningService
from src.business_cleaner.ec_goods_phone_cleaner import ECGoodsPhoneCleaner
from src.business_cleaner.ec_comment_cleaner import ECCommentCleaner
from src.business_cleaner.customer_dialog_cleaner import CustomerDialogCleaner


def test_ec_goods_phone():
    """测试电商商品清洗"""
    print("\n=== 测试电商商品数据清洗 ===")
    
    # 测试数据
    records = [
        {
            'product_id': 'P001',
            'product_name': '手机壳 <HTML>防摔</HTML>',
            'category': '手机配件',
            'price': '¥99.99',
            'sales': '1000+',
            'rating': '4.5/5',
            'description': '优质手机壳'
        },
        {
            'product_id': 'P002',
            'product_name': '充电器',
            'category': '充电设备',
            'price': '59.9',
            'sales': '500',
            'rating': '4.2',
            'description': '快速充电器'
        }
    ]
    
    result = ECGoodsPhoneCleaner.clean(records)
    print(f"原始记录数：{result['original_count']}")
    print(f"清洗后记录数：{result['cleaned_count']}")
    print(f"清洗记录：{json.dumps(result['records'], indent=2, ensure_ascii=False)}")
    print(f"统计信息：{json.dumps(result['statistics'], indent=2, ensure_ascii=False)}")


def test_ec_comment():
    """测试电商评论清洗"""
    print("\n=== 测试电商评论数据清洗 ===")
    
    # 测试数据
    records = [
        {
            'comment_id': 'C001',
            'product_id': 'P001',
            'user_id': 'U001',
            'content': '很好用，非常满意！😊😊 http://example.com',
            'rating': '5',
            'create_time': '2024-01-08 10:30:00',
            'helpful_count': '100'
        },
        {
            'comment_id': 'C002',
            'product_id': 'P001',
            'user_id': 'U002',
            'content': '不太满意，有问题 😢',
            'rating': '2',
            'create_time': '2024-01-08 11:00:00',
            'helpful_count': '50'
        }
    ]
    
    result = ECCommentCleaner.clean(records, enable_llm=False)
    print(f"原始记录数：{result['original_count']}")
    print(f"清洗后记录数：{result['cleaned_count']}")
    print(f"清洗记录：{json.dumps(result['records'], indent=2, ensure_ascii=False)}")
    print(f"统计信息：{json.dumps(result['statistics'], indent=2, ensure_ascii=False)}")


def test_customer_dialog():
    """测试客户对话清洗"""
    print("\n=== 测试客户对话数据清洗 ===")
    
    # 测试数据
    records = [
        {
            'dialog_id': 'D001',
            'customer_id': 'C001',
            'agent_id': 'A001',
            'messages': [
                {
                    'sender': 'customer',
                    'content': '你好，我想咨询一下产品信息',
                    'timestamp': '2024-01-08 10:00:00'
                },
                {
                    'sender': 'agent',
                    'content': '您好，请问您想了解哪个产品？',
                    'timestamp': '2024-01-08 10:01:00'
                }
            ],
            'sentiment': 'neutral',
            'topic': 'inquiry',
            'duration': 300
        }
    ]
    
    result = CustomerDialogCleaner.clean(records, enable_llm=False)
    print(f"原始记录数：{result['original_count']}")
    print(f"清洗后记录数：{result['cleaned_count']}")
    print(f"清洗记录：{json.dumps(result['records'], indent=2, ensure_ascii=False)}")
    print(f"统计信息：{json.dumps(result['statistics'], indent=2, ensure_ascii=False)}")


def test_get_business_types():
    """测试获取支持的业务类型"""
    print("\n=== 测试获取业务类型列表 ===")
    
    response = MCPDataCleaningService.get_supported_business_types()
    print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    print(f"MCP数据清洗服务测试 - {datetime.now()}")
    print("=" * 50)
    
    test_ec_goods_phone()
    test_ec_comment()
    test_customer_dialog()
    test_get_business_types()
    
    print("\n" + "=" * 50)
    print("测试完成！")
