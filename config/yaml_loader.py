# -*- coding: utf-8 -*-
"""
YAML 配置加载器

根据 RUN_MODE 环境变量加载对应的 YAML 配置文件。
统一处理环境变量和 YAML 配置的读取。
"""

import os
import yaml
from typing import Dict, Any
import re
from pathlib import Path

# 加载 .env 文件中的环境变量
try:
    from dotenv import load_dotenv
    # 在项目根目录查找 .env 文件
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path), override=False)
except ImportError:
    pass

# 获取运行模式（默认开发）
RUN_MODE = os.getenv("RUN_MODE", "dev").lower()

# 标准化运行模式（支持短形式和长形式）
RUN_MODE_MAP = {
    "dev": "dev",
    "development": "dev",
    "test": "test",
    "testing": "test",
    "prod": "prod",
    "production": "prod"
}

if RUN_MODE not in RUN_MODE_MAP:
    raise ValueError(
        f"不支持的运行模式：{RUN_MODE}\n"
        f"支持的模式：dev, development, test, testing, prod, production"
    )

RUN_MODE = RUN_MODE_MAP[RUN_MODE]

# 确定配置文件路径
CONFIG_DIR = os.path.join(os.path.dirname(__file__))

if RUN_MODE == "prod":
    CONFIG_FILE = os.path.join(CONFIG_DIR, "prod.yaml")
elif RUN_MODE == "test":
    CONFIG_FILE = os.path.join(CONFIG_DIR, "test.yaml")
else:  # dev
    CONFIG_FILE = os.path.join(CONFIG_DIR, "dev.yaml")


def _substitute_env_vars(value: Any) -> Any:
    """
    递归替换字符串中的环境变量占位符
    支持 ${VAR} 和 ${VAR:default} 两种格式
    """
    if isinstance(value, str):
        # 匹配 ${VAR} 或 ${VAR:default}
        def replace_var(match):
            full_match = match.group(0)  # ${VAR} 或 ${VAR:default}
            var_expr = match.group(1)    # VAR 或 VAR:default
            
            if ":" in var_expr:
                var_name, default_val = var_expr.split(":", 1)
                return os.getenv(var_name.strip(), default_val.strip())
            else:
                return os.getenv(var_expr.strip(), "")
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, value)
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(item) for item in value]
    return value


def load_config() -> Dict[str, Any]:
    """
    加载 YAML 配置文件并替换环境变量
    """
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"配置文件不存在：{CONFIG_FILE}")
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if config is None:
            config = {}
        
        # 替换配置中的环境变量
        config = _substitute_env_vars(config)
        
        return config
    
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 配置文件格式错误：{CONFIG_FILE}\n{e}")
    except Exception as e:
        raise RuntimeError(f"加载配置文件失败：{CONFIG_FILE}\n{e}")


# 全局配置对象
_config = None


def get_config() -> Dict[str, Any]:
    """获取全局配置对象"""
    global _config
    if _config is None:
        _config = load_config()
        print(f"[OK] 已加载 {RUN_MODE.upper()} 环境配置：{CONFIG_FILE}")
    return _config


# 便利函数：获取嵌套配置值
def get(key_path: str, default=None) -> Any:
    """
    获取配置值，支持点号分隔的路径
    
    例：
        get("database.host") → "mysql"
        get("app.version") → "1.0.0"
        get("nonexistent", "default_value") → "default_value"
    """
    config = get_config()
    keys = key_path.split(".")
    value = config
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value if value is not None else default


# 便利函数：获取数据库配置
def get_db_config() -> Dict[str, Any]:
    """获取数据库配置"""
    return get_config().get("database", {})


# 便利函数：获取日志配置
def get_log_config() -> Dict[str, Any]:
    """获取日志配置"""
    return get_config().get("logging", {})


# ... existing code ...

# 便利函数：获取API配置
def get_api_config() -> Dict[str, Any]:
    """获取API配置"""
    return get_config().get("api", {})


# 便利函数：获取阿里云配置
def get_aliyun_config() -> Dict[str, Any]:
    """获取阿里云配置"""
    return get_config().get("aliyun", {})
if RUN_MODE not in ["dev", "test", "prod"]:
    raise ValueError(
        f"不支持的运行模式：{RUN_MODE}\n"
        f"支持的模式：dev, test, prod"
    )
