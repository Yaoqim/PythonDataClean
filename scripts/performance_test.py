# -*- coding: utf-8 -*-
"""
性能测试脚本

测试数据清洗服务的性能指标：
- 吞吐量 (records/sec)
- 内存占用
- 清洗耗时
- 数据库入库速度

执行方式: python scripts/performance_test.py
"""

import sys
import os
import time
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import tracemalloc

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.business_cleaner.ec_goods_phone_cleaner import ECGoodsPhoneCleaner
from src.business_cleaner.ec_comment_cleaner import ECCommentCleaner
from src.business_cleaner.customer_dialog_cleaner import CustomerDialogCleaner

logger = get_logger(__name__)


class PerformanceTest:
    """性能测试类"""
    
    @staticmethod
    def generate_test_data(count: int, data_type: str = 'goods') -> list:
        """生成测试数据"""
        if data_type == 'goods':
            return [
                {
                    'product_id': f'P{i:06d}',
                    'product_name': f'商品名称 {i} <HTML>防摔</HTML>',
                    'category': random.choice(['手机配件', '充电设备', '屏幕保护']),
                    'price': f'¥{random.uniform(10, 999):.2f}',
                    'sales': f'{random.randint(100, 10000)}+',
                    'rating': f'{random.uniform(3, 5):.1f}/5',
                    'description': f'这是商品 {i} 的详细描述'
                }
                for i in range(count)
            ]
        elif data_type == 'comment':
            return [
                {
                    'comment_id': f'C{i:06d}',
                    'product_id': f'P{random.randint(0, count-1):06d}',
                    'user_id': f'U{random.randint(1, 1000)}',
                    'content': f'评论内容 {i} 😊😊 http://example.com',
                    'rating': random.randint(1, 5),
                    'create_time': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    'helpful_count': f'{random.randint(0, 1000)}'
                }
                for i in range(count)
            ]
        else:  # dialog
            return [
                {
                    'dialog_id': f'D{i:06d}',
                    'customer_id': f'C{random.randint(1, 500)}',
                    'agent_id': f'A{random.randint(1, 100)}',
                    'messages': [
                        {
                            'sender': 'customer' if j % 2 == 0 else 'agent',
                            'content': f'消息内容 {j}',
                            'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1000))).isoformat()
                        }
                        for j in range(random.randint(2, 10))
                    ],
                    'duration': random.randint(60, 3600)
                }
                for i in range(count)
            ]
    
    @staticmethod
    def test_cleaner(cleaner_class, data: list, cleaner_name: str, test_size: int):
        """测试清洗器性能"""
        print(f"\n{'=' * 60}")
        print(f"测试: {cleaner_name} (数据量: {test_size})")
        print(f"{'=' * 60}")
        
        # 内存追踪
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        # 计时
        start_time = time.time()
        
        # 执行清洗
        result = cleaner_class.clean(data, enable_llm=False)
        
        # 结束计时
        end_time = time.time()
        duration = end_time - start_time
        
        # 内存统计
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_used = (current - start_memory) / 1024 / 1024  # MB
        
        # 计算性能指标
        throughput = test_size / duration if duration > 0 else 0
        success_rate = (result['cleaned_count'] / result['original_count'] * 100) if result['original_count'] > 0 else 0
        
        # 输出结果
        print(f"\n✅ 清洗结果:")
        print(f"  原始记录数:     {result['original_count']:,}")
        print(f"  清洗后记录数:   {result['cleaned_count']:,}")
        print(f"  成功率:         {success_rate:.2f}%")
        print(f"\n📊 性能指标:")
        print(f"  总耗时:         {duration:.3f} 秒")
        print(f"  吞吐量:         {throughput:,.0f} 条/秒")
        print(f"  单条耗时:       {duration*1000/test_size:.3f} 毫秒")
        print(f"  内存占用:       {memory_used:.2f} MB")
        print(f"  内存效率:       {memory_used/test_size*1000000:.2f} Bytes/条")
        print(f"\n📈 质量指标:")
        print(f"  去重率:         {result['statistics']['dedup_rate']:.2%}")
        print(f"  缺失率:         {result['statistics']['missing_rate']:.2%}")
        
        return {
            'cleaner': cleaner_name,
            'duration': duration,
            'throughput': throughput,
            'memory_used_mb': memory_used,
            'success_rate': success_rate,
            'original_count': result['original_count'],
            'cleaned_count': result['cleaned_count'],
        }


def run_performance_tests():
    """运行所有性能测试"""
    print("\n" + "=" * 60)
    print("MCP数据清洗服务 性能测试")
    print("=" * 60)
    
    # 测试配置
    test_configs = [
        (1000, 'goods', ECGoodsPhoneCleaner, '电商商品清洗器'),
        (1000, 'comment', ECCommentCleaner, '电商评论清洗器'),
        (500, 'dialog', CustomerDialogCleaner, '客户对话清洗器'),
    ]
    
    results = []
    
    for test_size, data_type, cleaner_class, cleaner_name in test_configs:
        # 生成测试数据
        test_data = PerformanceTest.generate_test_data(test_size, data_type)
        
        # 运行测试
        result = PerformanceTest.test_cleaner(
            cleaner_class, 
            test_data, 
            cleaner_name, 
            test_size
        )
        results.append(result)
    
    # 汇总报告
    print(f"\n\n{'=' * 80}")
    print("性能测试总结")
    print(f"{'=' * 80}")
    print(f"{'清洗器':20} {'吞吐量(条/秒)':15} {'耗时(秒)':12} {'内存(MB)':12} {'成功率':10}")
    print(f"{'-' * 80}")
    
    total_duration = 0
    total_records = 0
    
    for r in results:
        print(f"{r['cleaner']:20} {r['throughput']:>14,.0f} {r['duration']:>11.3f} {r['memory_used_mb']:>11.2f} {r['success_rate']:>9.1f}%")
        total_duration += r['duration']
        total_records += r['original_count']
    
    print(f"{'-' * 80}")
    avg_throughput = total_records / total_duration if total_duration > 0 else 0
    print(f"{'总体平均':20} {avg_throughput:>14,.0f} {total_duration:>11.3f}")
    print(f"{'=' * 80}\n")
    
    return results


if __name__ == '__main__':
    run_performance_tests()
