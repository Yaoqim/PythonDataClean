# -*- coding: utf-8 -*-
"""
生成电商商品临时数据文件

生成 30 条真实电商商品数据文件，保存到 data/temp 目录
供完整流程测试使用
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根路径
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def generate_goods_data():
    """生成 30 条电商商品数据"""
    goods_data = []
    
    # 场景1: 标准记录 (5条)
    for i in range(1, 6):
        goods_data.append({
            'product_id': f'PROD_{i:03d}',
            'title': f'Apple iPhone 15 Pro Max 正品 {i}',
            'price': f'{8000 + i * 100}',
            'currency_code': 'CNY',
            'shop_name': '官方旗舰店',
            'source_platform': 'JD',
            'brand': 'Apple',
            'original_price': '10999',
            'rating': 4.8,
            'good_rate': 95.5,
            'sales_volume': 15000 + i * 100,
            'comment_count': 5200 + i * 50,
            'is_official': 1,
            'listing_time': '2024-01-01 10:00:00',
            'update_time': datetime.now().isoformat()
        })
    
    # 场景2: 不同货币 (3条)
    goods_data.append({
        'product_id': 'PROD_006',
        'title': 'Samsung Galaxy S24 Ultra',
        'price': '$999.99',
        'currency_code': 'USD',
        'shop_name': 'Amazon',
        'source_platform': 'Amazon',
        'rating': 4.5,
        'good_rate': 92.0,
        'sales_volume': 8500
    })
    
    goods_data.append({
        'product_id': 'PROD_007',
        'title': 'MacBook Pro 16英寸',
        'price': '€1899',
        'currency_code': 'EUR',
        'shop_name': 'Apple Store',
        'source_platform': 'JD',
        'rating': 4.9,
        'good_rate': 97.0
    })
    
    goods_data.append({
        'product_id': 'PROD_008',
        'title': '小米 14 Pro',
        'price': '3999',
        'currency_code': 'CNY',
        'shop_name': '小米官方',
        'source_platform': 'Taobao'
    })
    
    # 场景3: 标题冗长咏特殊字符 (2条)
    goods_data.append({
        'product_id': 'PROD_009',
        'title': 'iPad Pro 12.9" ✨ 最新款 🎉 性价比之选',
        'price': '5999',
        'currency_code': 'CNY',
        'shop_name': 'Apple专卖店',
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_010',
        'title': '  华为Mate 60 Pro   ',  # 空格测试
        'price': '4999',
        'currency_code': 'CNY',
        'shop_name': '华为官方',
        'source_platform': 'Taobao'
    })
    
    # 场景4: 销量含单位 (2条)
    goods_data.append({
        'product_id': 'PROD_011',
        'title': 'AirPods Pro 第二代',
        'price': '1899',
        'currency_code': 'CNY',
        'shop_name': 'Apple',
        'source_platform': 'JD',
        'sales_volume': '3.5万件'
    })
    
    goods_data.append({
        'product_id': 'PROD_012',
        'title': 'Apple Watch Series 9',
        'price': '2999',
        'currency_code': 'CNY',
        'shop_name': 'Apple',
        'source_platform': 'JD',
        'sales_volume': '12万+',
        'good_rate': 98.5
    })
    
    # 场景5: 缺失核心字段 (3条)
    goods_data.append({
        'product_id': '',  # 缺少product_id
        'title': 'OnePlus 12',
        'price': '4599',
        'currency_code': 'CNY',
        'shop_name': 'OnePlus',
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_014',
        'title': '',  # 缺少title
        'price': '3299',
        'currency_code': 'CNY',
        'shop_name': 'Xiaomi',
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_015',
        'title': 'vivo X100',
        'price': None,  # 缺少price
        'currency_code': 'CNY',
        'shop_name': 'vivo',
        'source_platform': 'JD'
    })
    
    # 场景6: 缺失非核心字段 (2条)
    goods_data.append({
        'product_id': 'PROD_016',
        'title': 'OPPO Find X7',
        'price': '4999',
        'currency_code': 'CNY',
        'shop_name': '',  # 缺少shop_name
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_017',
        'title': 'Google Pixel 8',
        'price': '6299',
        'currency_code': '',  # 缺少currency_code
        'shop_name': 'Google',
        'source_platform': 'JD'
    })
    
    # 场景7: 异常值 (3条)
    goods_data.append({
        'product_id': 'PROD_018',
        'title': 'Sony WH-1000XM5',
        'price': '-999',  # 负数
        'currency_code': 'CNY',
        'shop_name': 'Sony',
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_019',
        'title': '高端商务笔记本',
        'price': '9999999',  # 价格超出范围
        'currency_code': 'CNY',
        'shop_name': 'Dell',
        'source_platform': 'JD'
    })
    
    goods_data.append({
        'product_id': 'PROD_020',
        'title': 'JBL Flip 6',
        'price': '599',
        'currency_code': 'INVALID',  # 不效货币代码
        'shop_name': 'JBL',
        'source_platform': 'JD'
    })
    
    # 场景8: 重复记录 (2条)
    goods_data.append({
        'product_id': 'PROD_001',  # 重复的product_id
        'title': 'Apple iPhone 15 Pro Max',
        'price': '8999',
        'currency_code': 'CNY',
        'shop_name': '官方店',
        'source_platform': 'JD',
        'rating': 4.8,
        'update_time': (datetime.now() - timedelta(days=1)).isoformat()  # 旧记录
    })
    
    goods_data.append({
        'product_id': 'PROD_021',
        'title': 'Beats Studio Pro',
        'price': '2999',
        'currency_code': 'CNY',
        'shop_name': 'Beats',
        'source_platform': 'JD',
        'rating': 4.7
    })
    
    # 场景9: 时间格式化 (2条)
    goods_data.append({
        'product_id': 'PROD_022',
        'title': 'ASUS VivoBook',
        'price': '4999',
        'currency_code': 'CNY',
        'shop_name': 'ASUS',
        'source_platform': 'JD',
        'listing_time': '2024-01-01',  # 需要格式化
        'update_time': '3天前'  # 相对时间
    })
    
    goods_data.append({
        'product_id': 'PROD_023',
        'title': 'Lenovo ThinkPad',
        'price': '5999',
        'currency_code': 'CNY',
        'shop_name': 'Lenovo',
        'source_platform': 'JD',
        'good_rate': 120,  # 好评率不合法
        'rating': 9.5  # 评分不合法
    })
    
    # 场景10: 其他字段处理 (5条)
    goods_data.append({
        'product_id': 'PROD_024',
        'title': 'HP Pavilion',
        'price': '5499',
        'currency_code': 'CNY',
        'shop_name': 'HP',
        'source_platform': 'JD',
        'spec_params': '{"processor": "Intel i7", "ram": "16GB", "storage": "512GB SSD"}'
    })
    
    # 增加5条到30条
    for i in range(25, 30):
        goods_data.append({
            'product_id': f'PROD_{i:03d}',
            'title': f'第{i}个电子产品',
            'price': f'{3000 + i * 200}',
            'currency_code': 'CNY',
            'shop_name': f'店铺{i}',
            'source_platform': 'JD',
            'brand': f'品牌{i}',
            'rating': 4.5 + (i % 5) * 0.1,
            'good_rate': 90 + (i % 10),
            'sales_volume': 5000 + i * 100,
            'comment_count': 2000 + i * 50,
            'is_official': i % 2,
            'listing_time': (datetime.now() - timedelta(days=i)).isoformat(),
            'update_time': datetime.now().isoformat()
        })
    
    return goods_data


def main():
    """主函数"""
    # 创建 data/temp 目录
    data_dir = Path(project_root) / 'data' / 'temp'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成数据
    goods_data = generate_goods_data()
    
    # 验证数据条数
    assert len(goods_data) == 30, f"数据条数应为30条，实际{len(goods_data)}条"
    
    # 生成文件名（符合规范：业务类型_日期_序号.扩展名）
    today = datetime.now().strftime('%Y%m%d')
    data_file = data_dir / f'EC_GOODS_PHONE_{today}_0001.json'
    metadata_file = data_dir / f'EC_GOODS_PHONE_{today}_0001.metadata.json'
    
    # 保存数据文件
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(goods_data, f, ensure_ascii=False, indent=2)
    
    # 保存元数据文件
    metadata = {
        'business_type_id': 'EC_GOODS_PHONE',
        'data_structure_type': '结构化',
        'file_size_mb': round(data_file.stat().st_size / 1024 / 1024, 2),
        'data_carrier_type': 'JSON',
        'estimated_record_count': 30,
        'crawl_date': today,
        'data_source': '京东商城',
        'actual_record_count': 30,
        'crawl_tool': 'generate_temp_data',
        'checksum': 'mock_checksum_value'
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # 打印结果
    print("✓ 临时数据文件生成成功！")
    print(f"  数据文件：{data_file}")
    print(f"  元数据文件：{metadata_file}")
    print(f"  记录条数：{len(goods_data)}")
    print("\n你可以使用以下路径进行完整流程测试：")
    print(f"  {data_file}")
    print("\n服务将自动：")
    print("  1. 读取文件")
    print("  2. 验证元数据")
    print("  3. 执行数据清洗")
    print("  4. 存储到数据库")


if __name__ == '__main__':
    main()
