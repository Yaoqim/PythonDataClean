# 数据清洗 MCP 使用规范

## 文档概述

本项目 **数据清洗MCP** 是一个独立的数据处理服务，专门用于清洗结构化数据。本规范定义了如何请求、调用和集成本MCP，便于其他工作流或系统使用。

**核心理念**：
- 方法按单一、专注于数据清洗，不推态多元化
- 输入只需提供数据文件路径和元数据
- 清洗后的数据直接写入数据库，不返回文件给工作流
- 服务端自动识别业务类型，无需指定清洗规则

---

## 第一部分：快速开始

### 1.1 最小化请求

```json
{
  "file_paths": [
    "/aliyun/data/EC_GOODS_PHONE_20240108_0001.json"
  ]
}
```

**就这么简单！** 服务端会：
1. 自动查找同名的 `.metadata.json` 文件
2. 自动识别业务类型和数据结构
3. 自动选择清洗规则
4. 执行完整的清洗流程

---

## 第二部分：请求规范

### 2.1 请求格式

```json
{
  "request_id": "req_20240108_001_abc123",
  "operation": "clean",
  "inputs": {
    "file_paths": [
      "/aliyun/data/EC_GOODS_PHONE_20240108_0001.json",
      "/aliyun/data/EC_GOODS_PHONE_20240108_0002.json"
    ],
    "options": {
      "batch_size": 5000,
      "parallel": true,
      "max_workers": 4,
    }
  },
  "context": {
    "workflow_id": "wf_20240108_001",
    "upstream_service": "data_crawler",
  }
}
```

### 2.2 请求字段说明

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| **request_id** | string | 是 | - | 唯一请求ID，用于日志追踪，格式：`req_YYYYMMDD_序号_随机码` |
| **operation** | string | 是 | - | 固定值为 `clean` |
| **inputs.file_paths** | string[] | 是 | - | 待清洗文件路径数组，支持1个或多个文件 |
| **inputs.options.batch_size** | int | 否 | 5000 | 批处理大小，根据内存调整 |
| **inputs.options.parallel** | bool | 否 | true | 是否启用并行处理 |
| **inputs.options.max_workers** | int | 否 | 4 | 最大并行数，建议不超过CPU核心数 |
| **context.workflow_id** | string | 否 | - | 所属工作流ID，用于追踪完整流程 |
| **context.upstream_service** | string | 否 | - | 上游服务名，如 `data_crawler` |

### 2.3 元数据文件要求

每个数据文件必须有对应的 `.metadata.json` 文件，位于同一目录，名称相同但后缀不同。

**文件对应关系：**
- 数据文件：`EC_GOODS_PHONE_20240108_0001.json`
- 元数据文件：`EC_GOODS_PHONE_20240108_0001.metadata.json`

**元数据文件内容：**

```json
{
  "business_type_id": "EC_GOODS_PHONE",
  "business_type_name": "电商商品-手机",
  "data_structure_type": "结构化",
  "data_carrier_type": "JSON",
  "file_size_mb": 50,
  "estimated_record_count": 10000,
  "actual_record_count": 9856,
  "crawl_date": "20240108",
  "data_source": "京东商城",
  "crawl_tool": "Scrapy",
  "checksum": "abc123def456"
}
```

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| **business_type_id** | 是 | 业务类型唯一标识，对应清洗规则配置 |
| **business_type_name** | 是 | 业务类型名称，便于识别 |
| **data_structure_type** | 是 | 数据结构类型：`结构化` / `半结构化` / `非结构化` |
| **data_carrier_type** | 是 | 数据载体类型：`JSON` / `CSV` / `XML` / `PDF` |
| **file_size_mb** | 是 | 文件大小（MB），影响处理策略选择 |
| **estimated_record_count** | 是 | 预估记录数，用于优化批处理参数 |
| **actual_record_count** | 否 | 实际记录数（可选） |
| **crawl_date** | 是 | 数据抓取日期，格式 `YYYYMMDD` |
| **data_source** | 是 | 数据来源名称 |
| **crawl_tool** | 是 | 抓取工具名称 |
| **checksum** | 否 | 文件完整性校验值 |

---

## 第三部分：响应规范

### 3.1 成功响应

```json
{
  "request_id": "req_20240108_001_abc123",
  "status": "success",
  "timestamp": "2024-01-08T10:30:45Z",
  "msg": "所有文件清洗成功并入库",
  "result": {
    "files_processed": 1,
    "files_successful": 1,
    "files_failed": 0,
    "storage_info": [
      {
        "business_type_id": "EC_GOODS_PHONE",
        "table_name": "ec_goods_info",
        "records_inserted": 9856,
        "table_location": "Database: data_clean, Table: ec_goods_info",
        "key_fields": ["product_id", "title", "price", "currency_code", "shop_name"],
        "time_range": "2024-01-08 to 2024-01-08"
      }
    ]
  }
}
```

### 3.2 错误响应

```json
{
  "request_id": "req_20240108_001_abc123",
  "status": "failed",
  "timestamp": "2024-01-08T10:30:45Z",
  "error_code": "11002",
  "msg": "元数据文件不存在：/aliyun/data/EC_GOODS_PHONE_20240108_0001.metadata.json"
}
```

### 3.3 部分成功响应

```json
{
  "request_id": "req_20240108_001_abc123",
  "status": "partial_success",
  "timestamp": "2024-01-08T10:30:45Z",
  "msg": "部分文件处理成功",
  "result": {
    "files_processed": 2,
    "files_successful": 1,
    "files_failed": 1,
    "failed_files": [
      {
        "file_path": "/aliyun/data/EC_GOODS_PHONE_20240108_0002.json",
        "error_code": "11003",
        "msg": "JSON格式错误：无效的JSON格式"
      }
    ]
  }
}
```

### 3.2.1 错误响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| **request_id** | string | 同请求ID，用于追踪 |
| **status** | string | 固定值 `failed` |
| **timestamp** | string | 响应时间戳（ISO 8601格式） |
| **error_code** | string | 错误代码，10000+ 开头，见错误代码表 |
| **msg** | string | 错误信息说明，如 "元数据文件不存在：/path/to/file" |

### 3.3.1 成功响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| **request_id** | string | 同请求ID，用于追踪 |
| **status** | string | 固定值 `success` |
| **timestamp** | string | 响应时间戳（ISO 8601格式） |
| **msg** | string | 成功提示信息，清洗数据已直接入库 |
| **result** | object | 处理结果统计 |
| **result.files_processed** | int | 处理的文件总数 |
| **result.files_successful** | int | 成功处理的文件数 |
| **result.files_failed** | int | 失败的文件数 |
| **result.storage_info** | array | 数据存储位置信息（供后续打标使用） |
| **result.storage_info[].business_type_id** | string | 业务类型ID |
| **result.storage_info[].table_name** | string | 数据库表名 |
| **result.storage_info[].records_inserted** | int | 插入的记录数 |
| **result.storage_info[].table_location** | string | 数据库位置描述（格式：Database: db_name, Table: table_name） |
| **result.storage_info[].key_fields** | array | 关键字段列表（便于后续查询和打标） |
| **result.storage_info[].time_range** | string | 数据时间范围 |

> **注意**：清洗后的数据直接写入数据库，不返回文件给工作流。本MCP功能单一，专注于数据清洗。如需生成文件，这是后续扩展功能。

### 3.3.2 部分成功响应字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| **request_id** | string | 同请求ID，用于追踪 |
| **status** | string | 固定值 `partial_success` |
| **timestamp** | string | 响应时间戳（ISO 8601格式） |
| **msg** | string | 提示信息 |
| **result** | object | 处理结果统计 |
| **result.files_processed** | int | 处理的文件总数 |
| **result.files_successful** | int | 成功处理的文件数（已入库） |
| **result.files_failed** | int | 失败的文件数 |
| **result.failed_files** | array | 失败的文件列表 |
| **result.failed_files[].file_path** | string | 失败的文件路径 |
| **result.failed_files[].error_code** | string | 错误代码（10000+） |
| **result.failed_files[].msg** | string | 错误信息说明 |
| **result.storage_info** | array | 数据存储位置信息（供后续打标使用） |
| **result.storage_info[].business_type_id** | string | 业务类型ID |
| **result.storage_info[].table_name** | string | 数据库表名 |
| **result.storage_info[].records_inserted** | int | 插入的记录数 |
| **result.storage_info[].table_location** | string | 数据库位置描述（格式：Database: db_name, Table: table_name） |
| **result.storage_info[].key_fields** | array | 关键字段列表（便于后续查询和打标） |
| **result.storage_info[].time_range** | string | 数据时间范围 |

### 3.2.2 业务错误码体系

本MCP使用 **业务错误码体系**，从 **10000** 开始编号，避免与HTTP状态码冲突，并为各业务类型预留扩展空间。

#### 错误码段划分

| 错误段 | 范围 | 说明 |
| --- | --- | --- |
| 通用错误 | 10000-10999 | 与业务类型无关的通用错误 |
| 文件和元数据错误 | 11000-11999 | 文件读写、格式、编码等错误 |
| 数据库错误 | 12000-12999 | 数据库连接、操作、事务等错误 |
| 清洗流程错误 | 13000-13999 | 数据清洗过程中的业务逻辑错误 |
| 电商业务专用错误 | 20000-20999 | 电商类型（EC_）业务特有错误（预留） |
| 社交业务专用错误 | 21000-21999 | 社交类型（SOCIAL_）业务特有错误（预留） |
| 资讯业务专用错误 | 22000-22999 | 资讯类型（NEWS_）业务特有错误（预留） |
| 财务业务专用错误 | 23000-23999 | 财务类型（FINANCE_）业务特有错误（预留） |
| 其他业务专用错误 | 30000+ | 其他业务类型专用错误（预留） |

#### 通用错误码（10000-10999）

| 错误码 | HTTP状态 | 错误名称 | 说明 | 解决方案 |
| --- | --- | --- | --- | --- |
| **10001** | 400 | `INVALID_REQUEST` | 请求格式无效（缺少必要字段） | 检查request_id、operation、inputs字段是否完整 |
| **10002** | 400 | `INVALID_PARAMETERS` | 请求参数值错误 | 检查batch_size > 0、max_workers合理、timeout_seconds有效 |
| **10003** | 400 | `INVALID_BUSINESS_TYPE` | 业务类型不支持 | 检查metadata中business_type_id是否在支持列表中 |
| **10004** | 504 | `PROCESSING_TIMEOUT` | 处理超时（超过timeout_seconds） | 减少batch_size、增加timeout_seconds或改为异步 |
| **10005** | 500 | `INSUFFICIENT_MEMORY` | 内存不足，无法完成处理 | 减少batch_size、关闭parallel或分多次处理 |
| **10006** | 500 | `SERVICE_UNAVAILABLE` | 服务暂时不可用 | 稍后重试或检查服务状态 |

#### 文件和元数据错误码（11000-11999）

| 错误码 | HTTP状态 | 错误名称 | 说明 | 解决方案 |
| --- | --- | --- | --- | --- |
| **11001** | 500 | `DATA_FILE_NOT_FOUND` | 数据文件不存在 | 检查file_paths路径是否正确、文件是否上传 |
| **11002** | 500 | `METADATA_FILE_NOT_FOUND` | 元数据文件不存在 | 检查是否存在同名.metadata.json文件 |
| **11003** | 500 | `METADATA_FORMAT_ERROR` | 元数据文件非JSON格式 | 确保.metadata.json为有效JSON格式 |
| **11004** | 500 | `METADATA_MISSING_REQUIRED_FIELD` | 元数据缺少必要字段 | 检查metadata中是否包含business_type_id、data_structure_type等 |
| **11005** | 500 | `DATA_FORMAT_ERROR` | 数据文件格式无效 | 检查JSON/CSV格式是否有效，是否包含语法错误 |
| **11006** | 500 | `ENCODING_ERROR` | 文件编码错误 | 确保文件使用UTF-8编码，不使用其他编码如GBK |
| **11007** | 500 | `FILE_TOO_LARGE` | 文件过大，超过限制 | 检查file_size_mb、分割文件或增加处理资源 |
| **11008** | 500 | `FILE_READ_PERMISSION_DENIED` | 无法读取文件（权限问题） | 检查文件权限、所有者是否正确 |
| **11009** | 500 | `INVALID_FILE_PATH` | 文件路径格式无效 | 使用绝对路径，避免特殊字符或空格 |

#### 数据库错误码（12000-12999）

| 错误码 | HTTP状态 | 错误名称 | 说明 | 解决方案 |
| --- | --- | --- | --- | --- |
| **12001** | 500 | `DATABASE_CONNECTION_FAILED` | 无法连接到数据库 | 检查database_config中的host、port、credentials是否正确 |
| **12002** | 500 | `DATABASE_AUTHENTICATION_FAILED` | 数据库认证失败 | 检查用户名、密码是否正确 |
| **12003** | 500 | `DATABASE_UNAVAILABLE` | 数据库暂时不可用 | 检查数据库服务是否运行 |
| **12004** | 500 | `TABLE_NOT_FOUND` | 目标表不存在 | 检查table_name是否存在，必要时创建表 |
| **12005** | 500 | `INSERT_FAILED` | 数据插入失败 | 检查字段映射、数据类型、约束是否正确 |
| **12006** | 500 | `DUPLICATE_KEY_ERROR` | 主键冲突 | 检查是否有重复数据、主键设置是否正确 |
| **12007** | 500 | `INSUFFICIENT_DISK_SPACE` | 数据库磁盘空间不足 | 清理数据库、增加磁盘空间 |
| **12008** | 500 | `TRANSACTION_ROLLBACK` | 事务回滚 | 检查错误日志，可能是数据完整性约束问题 |
| **12009** | 500 | `COLUMN_MISMATCH` | 字段映射错误 | 检查field_mapping中的字段名是否与表结构一致 |
| **12010** | 500 | `DATA_TYPE_MISMATCH` | 数据类型不匹配 | 检查输入数据类型是否与表定义一致 |

#### 清洗流程错误码（13000-13999）

| 错误码 | HTTP状态 | 错误名称 | 说明 | 解决方案 |
| --- | --- | --- | --- | --- |
| **13001** | 500 | `NO_DATA_TO_PROCESS` | 数据为空 | 检查输入数据是否为空，或元数据中的record_count是否准确 |
| **13002** | 500 | `MISSING_REQUIRED_FIELDS` | 关键字段缺失 | 检查must_clean_fields中的必填字段是否存在 |
| **13003** | 500 | `NORMALIZATION_FAILED` | 字段标准化失败 | 检查field_standard_rule的转换规则是否适用 |
| **13004** | 500 | `MISSING_VALUE_HANDLER_FAILED` | 缺失值处理失败 | 检查missing_value_handle策略是否可行 |
| **13005** | 500 | `ABNORMAL_VALUE_DETECTION_FAILED` | 异常值检测失败 | 查看详细错误，检查数据是否超出预期范围 |
| **13006** | 500 | `INVALID_CLEANING_RULE` | 清洗规则无效或不匹配 | 检查清洗规则配置是否与业务类型匹配 |
| **13007** | 500 | `DEDUPLICATION_FAILED` | 去重处理失败 | 检查唯一标识字段是否存在、是否正确设置 |
| **13008** | 500 | `QUALITY_CHECK_FAILED` | 数据质量检查未通过 | 检查data_quality_check条件，清洗结果是否达标 |
| **13009** | 500 | `RULE_CONFIG_NOT_FOUND` | 业务类型的清洗规则配置不存在 | 确认业务类型ID是否已配置清洗规则 |

#### 业务类型专用错误码示例（预留）

**电商业务错误（20000-20999）**
- 20001: `EC_PRODUCT_ID_INVALID` - 商品ID格式无效
- 20002: `EC_PRICE_PARSING_ERROR` - 价格解析错误
- 20003: `EC_INVENTORY_MISMATCH` - 库存不一致

**社交业务错误（21000-21999）**
- 21001: `SOCIAL_USER_ID_INVALID` - 用户ID格式无效
- 21002: `SOCIAL_COMMENT_LENGTH_ERROR` - 评论长度异常
- 21003: `SOCIAL_SENTIMENT_ANALYSIS_FAILED` - 情感分析失败

---

## 第四部分：业务类型与清洗规则

### 4.1 支持的业务类型

| 业务类型ID | 名称 | 数据结构 | 复杂度 | 文档 |
| --- | --- | --- | --- | --- |
| `EC_GOODS_PHONE` | 电商商品-手机 | 结构化 | ⭐⭐ | [电商平台数据.md](bussesType/业务类型_1电商平台数据.md) |
| `EC_COMMENT` | 电商商品评论 | 半结构化 | ⭐⭐⭐ | [电商商品评论.md](bussesType/业务类型_2电商商品评论.md) |
| `SOCIAL_COMMENT` | 社交平台评论 | 半结构化 | ⭐⭐⭐⭐ | [社交平台评论.md](bussesType/业务类型_3社交平台评论.md) |
| `SOCIAL_POST` | 社交平台帖子 | 半结构化 | ⭐⭐⭐⭐ | [社交平台帖子.md](bussesType/业务类型_4社交平台帖子.md) |
| `NEWS_ARTICLE` | 资讯文章 | 半结构化 | ⭐⭐⭐ | [资讯文章.md](bussesType/业务类型_5资讯文章.md) |
| `FINANCE_REPORT` | 财务报表 | 结构化 | ⭐⭐⭐⭐ | [财务报表.md](bussesType/业务类型_6财务报表.md) |
| `ENTERPRISE_INFO` | 企业工商信息 | 结构化 | ⭐⭐ | [企业工商信息.md](bussesType/业务类型_7企业工商信息.md) |
| `RECRUIT_JOB` | 招聘岗位 | 结构化 | ⭐⭐⭐ | [招聘岗位.md](bussesType/业务类型_8招聘岗位信息.md) |
| `VIDEO_METADATA` | 短视频元数据 | 结构化 | ⭐⭐ | [短视频元数据.md](bussesType/业务类型_9短视频元数据.md) |
| `USER_PROFILE` | 用户基础信息 | 结构化 | ⭐⭐⭐ | [用户基础信息.md](bussesType/业务类型_10用户基础信息.md) |
| `PROPERTY_INFO` | 房产信息 | 结构化 | ⭐⭐⭐ | [房产信息.md](bussesType/业务类型_11房产信息.md) |
| `CAR_INFO` | 汽车信息 | 结构化 | ⭐⭐⭐ | [汽车信息.md](bussesType/业务类型_12汽车信息.md) |
| `PURCHASE_ORDER` | 采购订单信息 | 结构化 | ⭐⭐⭐ | [采购订单信息.md](bussesType/业务类型_13采购订单信息.md) |

### 4.2 查看清洗规则

每个业务类型的详细清洗规则见上表"文档"列。规则包括：
- **字段定义**：英文名、中文名、数据类型、处理方式
- **特殊处理**：转换规则、验证规则、关联规则
- **清洗流程**：4个阶段，共10+个清洗策略
- **缺失值补充**：分级补充方案
- **存储建议**：数据库表结构和索引

---

## 第五部分：调用示例

### 5.1 Python 调用示例

```python
import requests
import json

# MCP服务端点
MCP_URL = "http://localhost:8000/clean"

# 构建请求
request = {
    "request_id": "req_20240108_001_abc123",
    "operation": "clean",
    "inputs": {
        "file_paths": [
            "/aliyun/data/EC_GOODS_PHONE_20240108_0001.json"
        ],
        "options": {
            "batch_size": 5000,
            "parallel": True,
            "max_workers": 4
        }
    },
    "context": {
        "workflow_id": "wf_20240108_001",
        "upstream_service": "data_crawler"
    }
}

# 发送请求
response = requests.post(MCP_URL, json=request, timeout=300)

# 处理响应
if response.status_code == 200:
    result = response.json()
    print(f"清洗成功！{result['result']['files_successful']}个文件")
    if result['result']['files_failed'] > 0:
        print(f"失败文件: {result['result']['failed_files']}")
else:
    print(f"错误: {response.json()}")
```

### 5.2 Shell 命令行调用

```bash
# 简单请求
curl -X POST http://localhost:8000/clean \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_20240108_001",
    "operation": "clean",
    "inputs": {
      "file_paths": ["/data/EC_GOODS_PHONE_20240108_0001.json"]
    }
  }'

# 保存结果到文件
curl -X POST http://localhost:8000/clean \
  -H "Content-Type: application/json" \
  -d @- > response.json << 'EOF'
{
  "request_id": "req_20240108_001",
  "operation": "clean",
  "inputs": {
    "file_paths": ["/data/EC_GOODS_PHONE_20240108_0001.json"]
  }
}
EOF
```

### 5.3 工作流集成示例

```python
from workflow.engine import WorkflowEngine

# 定义工作流
# 注意: 本清洗MCP不返回文件，只写入数据库
workflow = {
    "workflow_id": "wf_ec_data_flow",
    "steps": [
        {
            "step_id": "step_1_fetch",
            "service": "data_crawler",
            "operation": "fetch",
            "params": {"source": "jd.com"}
        },
        {
            "step_id": "step_2_clean",
            "service": "data_cleaner",
            "operation": "clean",
            "inputs_from": "step_1_fetch.output"
            # 清洗后数据直接入库，不返回文件
        },
        {
            "step_id": "step_3_query",
            "service": "data_query",
            "operation": "query",
            "params": {"business_type_id": "EC_GOODS_PHONE"}
            # 需要查询清洗后的数据时，不是从清洗服务输出获取，而是从数据库查询
        }
    ]
}

# 执行工作流
engine = WorkflowEngine()
result = engine.execute(workflow)

# 录、检查清洗的结果
clean_result = result["step_2_clean"]
if clean_result["status"] == "success":
    print(f"清洗成功！处理了 {clean_result['result']['files_successful']} 个文件，数据已入库")
else:
    print(f"清洗失败：{clean_result['msg']}")
```

---

## 第六部分：常见问题

### Q1：元数据文件应该由谁创建？

**A：** 由上游服务（数据抓取MCP）创建。本清洗MCP仅读取元数据，不生成。

### Q2：如何添加新的业务类型？

**A：** 
1. 在 `bussesType/` 目录创建业务类型文档（参考已有文档格式）
2. 在 `config/metadata_rules/` 创建对应的清洗规则配置
3. 在业务类型表中注册新的 `business_type_id`

### Q3：处理大文件时出现内存溢出怎么办？

**A：** 调整请求参数：
```json
{
  "inputs": {
    "options": {
      "batch_size": 1000,      // 减少批大小
      "parallel": false         // 关闭并行
    }
  }
}
```

### Q4：清洗后的数据存储在哪里？

**A:** 清洗后的数据直接写入数据库（每个业务类型对应一个表）。表名为业务类型ID的小写形式，例如 `EC_GOODS_PHONE` → `ec_goods_phone` 表。

### Q5：清洗后的数据会保存多久？

**A:** 数据库数据永久保存（按业务需求）。清洗MCP只责责数据入库，不责责删除。

### Q6：如何查询清洗后的数据？

**A:** 这超出了本MCP的责任范围，应该由专端提供QueryMCP或数据库查询服务，供工作流向数据库查询。

---

## 第七部分：清洗流程详解

本MCP对所有业务类型统一遵循 **5 大核心步骤**：

### 步骤 1：明确清洗目标
- 从元数据识别 `business_type_id`
- 加载对应的清洗规则配置
- 确定 `must_clean_fields`（必清洗字段）

### 步骤 2：去重处理
- 按主键（如 `product_id`、`comment_id`）去重
- 保留最新版本（按 `update_time` 排序）
- 完全重复记录检测与删除

### 步骤 3：字段标准化
- **文本字段**：去空格、去特殊字符、统一编码
- **数值字段**：去单位、类型转换、范围验证
- **时间字段**：格式统一、时间戳转换
- **分类字段**：映射到标准值、去重

### 步骤 4：缺失值处理
- **核心字段**缺失率 < 10%：删除记录
- **核心字段**缺失率 ≥ 10%：标注"待补充"
- **非核心字段**：填充"未知"或众数

### 步骤 5：异常值修正
- **数值异常**：用中位数/平均值修正或标记
- **格式异常**：尝试修复，无法修复则删除
- **内容异常**：垃圾内容、广告内容直接删除

---

## 第八部分：性能指标

| 指标 | 目标值 |
| --- | --- |
| 单次处理数据量 | ≤ 100,000 条记录 |
| 处理速度 | 10,000 条记录 ≤ 30 秒 |
| 内存占用 | ≤ 2GB |
| 请求响应时间 | ≤ 300 秒 |
| 数据库写入速度 | ≥ 1,000 条/秒 |
| 清洗准确率 | ≥ 95% |

---

## 第九部分：部署与启动

### 9.1 系统要求
- Python 3.8+
- 内存：≥ 4GB
- 磁盘空间：临时文件≥ 100GB
- 数据库：PostgreSQL / MySQL

### 9.2 启动服务

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建必要目录
mkdir -p config/metadata_rules data/temp logs

# 3. 启动MCP服务
python main.py

# 4. 验证服务
curl http://localhost:8000/health
```

### 9.3 配置数据库

编辑 `config/database_config.py`：
```python
DATABASE_CONFIG = {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "data_clean",
    "user": "admin",
    "password": "password"
}
```

---

## 第十部分：监控与告警

### 10.1 关键指标

```bash
# 查看服务状态
curl http://localhost:8000/metrics

# 查看清洗失败率
curl http://localhost:8000/metrics/failure_rate

# 查看数据库写入速度
curl http://localhost:8000/metrics/db_write_speed
```

### 10.2 日志位置

```
logs/
├── cleaner.log          # 清洗日志
├── database.log         # 数据库操作日志
├── metadata.log         # 元数据加载日志
└── error.log            # 错误日志
```

---

## 快速参考

### 最小请求模板
```json
{"file_paths": ["/path/to/file.json"]}
```

### 完整请求模板
```json
{
  "request_id": "req_YYYYMMDD_001_xxx",
  "operation": "clean",
  "inputs": {
    "file_paths": ["/path/to/file.json"],
    "options": {"batch_size": 5000, "parallel": true}
  },
  "context": {"workflow_id": "wf_xxx"}
}
```

### 成功响应检查清单
- ✅ `status` = `success`
- ✅ `result.files_successful` > 0
- ✅ `result.files_failed` = 0
- ✅ 数据已入库（由专端数据库查询确认）

### 故障排查步骤
1. 检查元数据文件是否存在且格式正确
2. 检查业务类型ID是否支持
3. 查看 `logs/error.log` 获取详细错误信息
4. 确认数据库连接正常
5. 确认磁盘空间充足（临时文件≥文件大小的2倍）
