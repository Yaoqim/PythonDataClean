# 环境配置指南

所有环境启动方式**完全相同**，只需修改 `.env` 文件和对应的 YAML 配置即可。

---

## 🚀 统一启动方式（所有环境都一样）

```bash
# 1. 创建 .env 文件
cp .env.example .env

# 2. 编辑 .env，设置 RUN_MODE 和数据库密码
vim .env

# 3. 启动服务
docker-compose up -d

# 4. 初始化数据库（首次运行）
docker-compose exec -T api python scripts/init_db.py
```

---

## 📋 各环境配置

### 开发环境 (RUN_MODE=dev)

**.env 配置**：
```bash
RUN_MODE=dev
DB_PASSWORD=root
```

**特点**：MySQL 本地 + DEBUG 日志 + 无 LLM + 无并行

**config/dev.yaml**：已预配置，通常无需修改

---

### 测试环境 (RUN_MODE=test)

**.env 配置**：
```bash
RUN_MODE=test
DB_PASSWORD=
```

**特点**：SQLite + WARNING 日志 + 无 LLM + 无并行 + API 端口 5001

**config/test.yaml**：已预配置，通常无需修改

---

### 生产环境 (RUN_MODE=prod)

**.env 配置**：
```bash
RUN_MODE=prod
DB_PASSWORD=your_secure_password
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OPENAI_API_KEY=sk-xxxx...
```

**特点**：MySQL 远程 + INFO 日志 + 启用 LLM + 8 个 workers 并行

**config/prod.yaml**：已预配置，通常无需修改

---

## ⚙️ 修改核心配置

如需修改某个环境的配置（如日志级别、并行 workers 数等），直接编辑对应的 YAML 文件：

```bash
# 修改开发环境配置
vim config/dev.yaml

# 修改后重启
docker-compose restart api
```

**常见配置修改**：

```yaml
# 修改日志级别
logging:
  level: INFO      # DEBUG / INFO / WARNING

# 修改并行 workers
processing:
  max_workers: 16

# 修改数据库连接池
database:
  pool_size: 30
```

---

## 🔄 切换环境

```bash
# 1. 停止当前服务
docker-compose down

# 2. 修改 .env 中的 RUN_MODE（和其他配置）
vim .env

# 3. 启动新环境
docker-compose up -d
```

---

## 📊 配置对比

| 配置项 | 开发 | 测试 | 生产 |
|-------|------|------|------|
| RUN_MODE | development | testing | production |
| 数据库 | MySQL 本地 | SQLite | MySQL 远程 |
| 日志级别 | DEBUG | WARNING | INFO |
| LLM | ❌ | ❌ | ✅ |
| 并行处理 | ❌ | ❌ | ✅ (8) |
| API 端口 | 5000 | 5001 | 5000 |

---

## 🔒 安全建议

```bash
# 不要将 .env 提交到 Git
echo ".env" >> .gitignore

# 设置严格权限
chmod 600 .env

# 使用强密码
DB_PASSWORD=P@ssw0rd!Secure2024
```

---

## 📞 快速操作

```bash
# 查看日志
docker-compose logs -f api

# 进入容器
docker-compose exec api bash

# 查看当前配置
docker-compose exec -T api python -c "from config import yaml_loader; import json; print(json.dumps(yaml_loader.config, indent=2))"
```


