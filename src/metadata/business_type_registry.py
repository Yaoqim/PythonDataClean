# -*- coding: utf-8 -*-
"""
业务类型注册表

存储所有业务类型的配置信息
"""

from typing import Dict, Any, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BusinessTypeRegistry:
    """
    业务类型注册表
    
    存储业务类型配置：
    - 清洗规则
    - 字段映射
    - 存储表名
    - 数据质量标准
    """
    
    # 业务类型配置
    BUSINESS_TYPES = {
        'EC_GOODS_PHONE': {
            'name': '电商平台商品数据',
            'description': '从电商平台爬取的商品信息',
            'table_name': 'ec_goods_phone',
            'data_carrier_type': '商品',
            'fields': {
                'product_id': '商品ID',
                'product_name': '商品名称',
                'category': '商品分类',
                'price': '商品价格',
                'sales': '销售数量',
                'rating': '商品评分',
                'description': '商品描述'
            }
        },
        'EC_COMMENT': {
            'name': '电商平台评论数据',
            'description': '从电商平台爬取的用户评论',
            'table_name': 'ec_comment',
            'data_carrier_type': '评论',
            'fields': {
                'comment_id': '评论ID',
                'product_id': '商品ID',
                'user_id': '用户ID',
                'content': '评论内容',
                'rating': '评分',
                'create_time': '创建时间',
                'helpful_count': '有用数'
            }
        },
        'CUSTOMER_DIALOG': {
            'name': '客户对话数据',
            'description': '客户服务、声后等对话数据',
            'table_name': 'customer_dialog',
            'data_carrier_type': '对话',
            'fields': {
                'dialog_id': '对话 ID',
                'customer_id': '客户 ID',
                'agent_id': '客服 ID',
                'messages': '消息列表',
                'sentiment': '情感倾向',
                'topic': '对话主题',
                'duration': '对话时长'
            }
        },
        'SOCIAL_COMMENT': {
            'name': '社交平台评论数据',
            'description': '社交平台用户评论',
            'table_name': 'social_comment',
            'data_carrier_type': '评论',
            'fields': {'comment_id': '评论 ID', 'content': '评论内容'}
        },
        'SOCIAL_POST': {
            'name': '社交平台帖子数据',
            'description': '社交平台帖子内容',
            'table_name': 'social_post',
            'data_carrier_type': '帖子',
            'fields': {'post_id': '帖子 ID', 'content': '帖子内容'}
        },
        'NEWS_ARTICLE': {
            'name': '资詅文章数据',
            'description': '新闻、资詅文章',
            'table_name': 'news_article',
            'data_carrier_type': '文章',
            'fields': {'article_id': '文章 ID', 'title': '文章主题'}
        },
        'FINANCE_REPORT': {
            'name': '财务报表数据',
            'description': '上市公司财务报表',
            'table_name': 'finance_report',
            'data_carrier_type': '报表',
            'fields': {'report_id': '报表 ID', 'revenue': '收入'}
        },
        'ENTERPRISE_INFO': {
            'name': '企业工商信息',
            'description': '企业工商注册信息',
            'table_name': 'enterprise_info',
            'data_carrier_type': '企业',
            'fields': {'company_id': '公司 ID', 'company_name': '公司名程'}
        },
        'RECRUIT_JOB': {
            'name': '招聘岗位数据',
            'description': '招聘平台岗位信息',
            'table_name': 'recruit_job',
            'data_carrier_type': '岗位',
            'fields': {'job_id': '岗位 ID', 'job_title': '岗位名称'}
        },
        'VIDEO_METADATA': {
            'name': '短视频元数据',
            'description': '短视频平台元数据',
            'table_name': 'video_metadata',
            'data_carrier_type': '视频',
            'fields': {'video_id': '视频 ID', 'title': '视频标题'}
        },
        'USER_PROFILE': {
            'name': '用户基础信息',
            'description': '用户个人信息',
            'table_name': 'user_profile',
            'data_carrier_type': '用户',
            'fields': {'user_id': '用户 ID', 'username': '用户名'}
        },
        'PROPERTY_INFO': {
            'name': '房产信息数据',
            'description': '房产中介信息',
            'table_name': 'property_info',
            'data_carrier_type': '房产',
            'fields': {'property_id': '房产 ID', 'property_name': '房产名称'}
        },
        'CAR_INFO': {
            'name': '汽车信息数据',
            'description': '旧车中介信息',
            'table_name': 'car_info',
            'data_carrier_type': '二手汽车',
            'fields': {'car_id': '汽车 ID', 'model': '车的款式'}
        },
        'PURCHASE_ORDER': {
            'name': '采购订单数据',
            'description': '企业采购订单信息',
            'table_name': 'purchase_order',
            'data_carrier_type': '订单',
            'fields': {'order_id': '订单 ID', 'amount': '订单金额'}
        }
    }
    
    @staticmethod
    def get_business_type_config(business_type_id: str) -> Optional[Dict[str, Any]]:
        """
        获取业务类型配置
        
        Args:
            business_type_id: 业务类型ID
        
        Returns:
            业务类型配置字典
        """
        return BusinessTypeRegistry.BUSINESS_TYPES.get(business_type_id)
    
    @staticmethod
    def get_table_name(business_type_id: str) -> Optional[str]:
        """获取表名"""
        config = BusinessTypeRegistry.get_business_type_config(business_type_id)
        return config.get('table_name') if config else None
    
    @staticmethod
    def get_fields(business_type_id: str) -> Optional[Dict[str, str]]:
        """获取字段定义"""
        config = BusinessTypeRegistry.get_business_type_config(business_type_id)
        return config.get('fields') if config else None
    
    @staticmethod
    def is_valid_business_type(business_type_id: str) -> bool:
        """检查业务类型是否有效"""
        return business_type_id in BusinessTypeRegistry.BUSINESS_TYPES
    
    @staticmethod
    def list_business_types() -> list:
        """获取所有业务类型"""
        return list(BusinessTypeRegistry.BUSINESS_TYPES.keys())
