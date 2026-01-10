# -*- coding: utf-8 -*-
"""
阿里云OSS服务客户端

功能：
- 从阿里云OSS下载文件
- 上传文件到阿里云OSS
- 列表OSS中的文件
- 删除OSS中的文件
"""

from typing import Optional, List
import os
import tempfile
from pathlib import Path

from src.utils.logger import get_logger
from config import yaml_loader

logger = get_logger(__name__)

try:
    import oss2
    HAS_OSS_SDK = True
except ImportError:
    HAS_OSS_SDK = False
    logger.warning("未安装oss2库，请执行 pip install oss2 来启用阿里云OSS功能")


class AliyunOSSClient:
    """阿里云OSS客户端"""
    
    def __init__(self):
        self.auth = None
        self.bucket = None
        self.endpoint = None
        self.bucket_name = None
        self._init_client()
    
    def _init_client(self):
        """初始化OSS连接"""
        if not HAS_OSS_SDK:
            logger.error("OSS SDK未安装，无法使用阿里云服务")
            return
        
        try:
            aliyun_config = yaml_loader.get('aliyun', {})
            oss_config = aliyun_config.get('oss', {})
            
            self.endpoint = oss_config.get('endpoint')
            self.bucket_name = oss_config.get('bucketName')
            access_key_id = os.getenv('OSS_ACCESS_KEY_ID', '')
            access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET', '')
            
            if not all([self.endpoint, self.bucket_name, access_key_id, access_key_secret]):
                logger.error("阿里云OSS配置不完整")
                return
            
            self.auth = oss2.Auth(access_key_id, access_key_secret)
            self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
            
            logger.info(f"阿里云OSS客户端初始化成功，Bucket: {self.bucket_name}")
        
        except Exception as e:
            logger.error(f"初始化阿里云OSS客户端失败：{e}")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.bucket is not None and HAS_OSS_SDK
    
    def download_file(self, oss_path: str, local_path: str) -> bool:
        """从OSS下载文件到本地"""
        if not self.is_connected():
            logger.error("OSS客户端未连接")
            return False
        
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"从OSS下载文件：{oss_path} -> {local_path}")
            self.bucket.get_object_to_file(oss_path, local_path)
            logger.info(f"文件下载成功：{local_path}")
            return True
        except Exception as e:
            logger.error(f"文件下载失败：{oss_path}，错误：{e}")
            return False
    
    def upload_file(self, local_path: str, oss_path: str) -> bool:
        """上传文件到OSS"""
        if not self.is_connected():
            logger.error("OSS客户端未连接")
            return False
        
        try:
            logger.info(f"上传文件到OSS：{local_path} -> {oss_path}")
            self.bucket.put_object_from_file(oss_path, local_path)
            logger.info(f"文件上传成功：{oss_path}")
            return True
        except Exception as e:
            logger.error(f"文件上传失败：{local_path}，错误：{e}")
            return False
    
    def file_exists(self, oss_path: str) -> bool:
        """检查OSS中的文件是否存在"""
        if not self.is_connected():
            return False
        
        try:
            return self.bucket.object_exists(oss_path)
        except Exception as e:
            logger.error(f"检查文件存在性失败：{oss_path}，错误：{e}")
            return False
    
    def list_files(self, prefix: str = '') -> List[str]:
        """列出OSS中指定前缀的文件"""
        if not self.is_connected():
            logger.error("OSS客户端未连接")
            return []
        
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                files.append(obj.key)
            return files
        except Exception as e:
            logger.error(f"列出文件失败，前缀：{prefix}，错误：{e}")
            return []
    
    def delete_file(self, oss_path: str) -> bool:
        """删除OSS中的文件"""
        if not self.is_connected():
            logger.error("OSS客户端未连接")
            return False
        
        try:
            self.bucket.delete_object(oss_path)
            logger.info(f"文件删除成功：{oss_path}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败：{oss_path}，错误：{e}")
            return False
    
    def get_file_to_temp(self, oss_path: str) -> Optional[str]:
        """下载文件到临时目录"""
        try:
            temp_dir = tempfile.gettempdir()
            file_name = oss_path.split('/')[-1]
            local_path = os.path.join(temp_dir, file_name)
            
            if self.download_file(oss_path, local_path):
                return local_path
            return None
        except Exception as e:
            logger.error(f"下载到临时文件失败：{e}")
            return None
