import os
import json
import pandas as pd
from src.utils.logger import Logger
from src.metadata.metadata_loader import MetadataLoader
from src.cleaner.base_cleaner import BaseCleaner
from src.storage.db_handler import DatabaseHandler

logger = Logger.setup_logger(__name__)

def process_files(file_paths: list):
    """处理文件的主函数"""
    for file_path in file_paths:
        try:
            logger.info(f"开始处理文件: {file_path}")
            
            # 1. 加载元数据
            metadata_file = file_path.replace(".json", ".metadata.json")
            metadata = MetadataLoader.load_metadata(metadata_file)
            logger.info(f"已加载元数据: {metadata['business_type_id']}")
            
            # 2. 加载数据
            data = pd.read_json(file_path, encoding='utf-8')
            logger.info(f"已加载数据: {len(data)} 条记录")
            
            # 3. 执行清洗
            cleaner = BaseCleaner(metadata)
            cleaned_data = cleaner.clean(data)
            logger.info(f"清洗完成: {len(cleaned_data)} 条有效记录")
            
            # 4. 保存到数据库
            db_handler = DatabaseHandler()
            table_name = metadata.get("storage_config", {}).get("database_config", {}).get("table_name", "default_table")
            db_handler.save_data(cleaned_data, table_name)
            
            logger.info(f"文件处理完成: {file_path}")
            
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {e}")
            continue

def main():
    """主程序"""
    # 创建必要的目录
    os.makedirs("config/metadata_rules", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Python MCP 数据清洗服务启动")
    logger.info("服务就绪，等待请求")

if __name__ == "__main__":
    main()
