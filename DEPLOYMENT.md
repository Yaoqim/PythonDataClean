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
| PostgreSQL | 5432 | 数据库 |
| API | 5000 | MCP 清洗服务 |
| Redis | 6379 | 缓存（可选） |
| Prometheus | 9090 | 监控指标收集 |
| Grafana | 3000 | 监控仪表板 |

## 🚀 生产部署

### 环境配置

创建 `.env` 文件配置环境变量：

```bash
# 数据库配置
DB_TYPE=postgresql
DB_HOST=postgres  # Docker 环境使用 postgres，本地使用 localhost
DB_PORT=5432
DB_NAME=data_clean
DB_USER=admin
DB_PASSWORD=your_secure_password

# API 配置
API_HOST=0.0.0.0
API_PORT=5000
RUN_MODE=production

# 日志配置
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# LLM 配置（可选）
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

### 使用 Docker Compose 部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 配置数据库密码等

# 2. 启动所有服务
docker-compose -f docker-compose.yml up -d

# 3. 等待服务启动
sleep 30

# 4. 初始化数据库
docker-compose exec -T api python scripts/init_db.py

# 5. 验证服务
curl http://localhost:5000/health

# 6. 查看 Prometheus 指标
# 访问 http://localhost:9090

# 7. 查看 Grafana 仪表板
# 访问 http://localhost:3000 (admin/admin)
```

## 📊 监控和指标

### Prometheus 指标

所有关键指标已通过 Prometheus 客户端暴露：

- **清洗指标**：请求数、耗时、吞吐量、记录数
- **质量指标**：质量评分、去重率、缺失率
- **数据库指标**：操作耗时、入库记录数、连接池状态
- **API 指标**：请求数、耗时、状态码

### 访问方式

```
# Prometheus 查询接口
http://localhost:9090

# 指标导出接口
http://localhost:8000/metrics

# Grafana 仪表板
http://localhost:3000
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
│   ├── settings.py         # 全局设置
│   └── db_credentials.py   # 数据库凭证
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
└── monitoring/
    └── prometheus.yml      # Prometheus 配置
```

## 🛠️ 故障排查

### 服务无法启动

```bash
# 检查日志
docker-compose logs api

# 检查端口占用
lsof -i :5000

# 检查数据库连接
docker-compose exec postgres psql -U admin -d data_clean
```

### 数据库连接失败

```bash
# 验证 PostgreSQL 是否运行
docker-compose ps

# 重启数据库
docker-compose restart postgres

# 检查数据库日志
docker-compose logs postgres
```

### 监控无数据

```bash
# 验证 Prometheus 连接
curl http://localhost:8000/metrics

# 检查 Prometheus 配置
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml

# 重启 Prometheus
docker-compose restart prometheus
```

## 📈 性能优化建议

1. **数据库优化**
   - 为高频字段添加索引
   - 定期进行 VACUUM 和 ANALYZE
   - 调整连接池大小

2. **API 优化**
   - 启用响应压缩（gzip）
   - 添加响应缓存
   - 使用 CDN 加速静态资源

3. **清洗优化**
   - 启用批处理处理
   - 使用 LLM 缓存
   - 并行处理多个请求

4. **监控优化**
   - 调整 Prometheus 抓取间隔
   - 设置告警规则
   - 定期清理旧数据

## 📞 支持和反馈

- GitHub Issues: [项目地址]
- 文档: 查看 QUICK_START.md
- 性能基准: 运行 `python scripts/performance_test.py`

---

**最后更新**: 2026-01-09
**版本**: 1.0.0
