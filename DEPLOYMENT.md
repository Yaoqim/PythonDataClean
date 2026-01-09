# MCP 数据清洗服务 - 部署指南

## 📋 快速开始

### 方式1：本地开发运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/init_db.py

# 3. 运行性能测试
python scripts/performance_test.py

# 4. 启动服务
python app.py
```

服务将在 `http://localhost:5000` 启动

### 方式2：Docker 容器运行（推荐生产环境）

```bash
# 1. 构建镜像
docker build -t data-clean-api:latest .

# 2. 启动 Docker Compose 完整环境
docker-compose up -d

# 3. 初始化数据库（首次运行）
docker-compose exec api python scripts/init_db.py

# 4. 查看日志
docker-compose logs -f api
```

### Docker Compose 包含的服务

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | 数据库 |
| API | 5000 | MCP 清洗服务 |

## 🚀 生产部署

### 环境配置

创建 `.env` 文件配置环境变量：

```bash
# 数据库配置
RUN_MODE=prod
DB_PASSWORD=your_secure_password

# 阿里云配置
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
```

### 使用 Docker Compose 部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 配置数据库密码等

# 2. 启动所有服务
docker-compose up -d

# 3. 等待服务启动
sleep 30

# 4. 初始化数据库
docker-compose exec -T api python scripts/init_db.py

# 5. 验证服务
curl http://localhost:5000/health
```


## 🧪 性能测试

```bash
# 运行性能基准测试
python scripts/performance_test.py

# 输出示例：
# 清洗器                 吞吐量(条/秒)       耗时(秒)       内存(MB)        成功率
# 电商商品清洗器         2,500.00           0.400          25.50           100.0%
# 电商评论清洗器         1,800.00           0.556          30.25           100.0%
# 客户对话清洗器         800.00             0.625          45.75           100.0%
```

## 🔧 数据库初始化

```bash
# 自动创建所有表
python scripts/init_db.py

# 手动创建特定表（如需要）
python -c "
from scripts.init_db import TABLES_SCHEMA
print('表定义:', list(TABLES_SCHEMA.keys()))
"
```

## 📁 项目结构

```
PythonDataClean/
├── app.py                    # Flask 主应用
├── requirements.txt          # Python 依赖
├── Dockerfile               # Docker 镜像定义
├── docker-compose.yml       # Docker Compose 配置
│
├── config/                  # 配置模块
│   ├── yaml_loader.py     # YAML配置加载器
│   ├── dev.yaml           # 开发环境配置
│   ├── test.yaml          # 测试环境配置
│   ├── prod.yaml          # 生产环境配置
│   └── db_credentials.py  # 数据库凭证
│
├── src/                     # 源代码
│   ├── utils/              # 工具模块
│   ├── file_service/       # 文件操作
│   ├── metadata/           # 元数据处理
│   ├── db_service/         # 数据库服务
│   ├── ai_service/         # LLM 集成
│   ├── business_cleaner/   # 业务清洗器
│   ├── orchestrator/       # 流程编排
│   ├── monitoring/         # 监控系统
│   └── mcp_service.py      # MCP 服务
│
├── scripts/                 # 脚本
│   ├── init_db.py          # 数据库初始化
│   └── performance_test.py # 性能测试
│
└── docker-compose.yml       # Docker Compose 配置
```

## 🛠️ 故障排查

### 服务无法启动

```bash
# 检查日志
docker-compose logs api

# 检查端口占用
lsof -i :5000

# 检查数据库连接
docker-compose exec mysql mysql -u root -p data_clean
```

### 数据库连接失败

```bash
# 验证 MySQL 是否运行
docker-compose ps

# 重启数据库
docker-compose restart mysql

# 检查数据库日志
docker-compose logs mysql
```

## 📈 性能优化建议

1. **数据库优化**
   - 为高频字段添加索引
   - 调整连接池大小
   - 定期备份数据库

2. **API 优化**
   - 启用响应压缩（gzip）
   - 添加响应缓存
   - 使用 CDN 加速静态资源

3. **清洗优化**
   - 启用批处理处理
   - 使用 LLM 缓存
   - 并行处理多个请求

## 📞 支持和反馈

- GitHub Issues: [项目地址]
- 文档: 查看 QUICK_START.md
- 性能基准: 运行 `python scripts/performance_test.py`

---

**最后更新**: 2026-01-09
**版本**: 1.0.0
