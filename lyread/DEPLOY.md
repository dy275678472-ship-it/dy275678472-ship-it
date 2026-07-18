# LyRead 运维部署说明

服务器：`101.34.63.137`（`ubuntu` 用户，Docker 化部署）。域名 `lyread.cn` → nginx(443) → 后端容器 `127.0.0.1:8004`。

**Cloud Agent SSH 接入**：见 [`docs/lyread-ssh.md`](../docs/lyread-ssh.md)（与上海A/曼谷同一模式：公钥写入 `authorized_keys`）。

## 架构

```
nginx (443)
  ├── /                → /usr/share/nginx/html  (Vue3 SPA 静态文件)
  ├── /api/*, /ep/*    → 127.0.0.1:8004  (FastAPI 后端容器)
  └── /health, /robots.txt, /sitemap.xml → 8004
后端容器 lyread-backend-fix  (network: lyread-net)
  ├── MySQL  容器 lyread-mysql  (127.0.0.1:3306, volume lyread_mysql-data)
  └── DeepSeek API (https://api.deepseek.com/v1)  ← 创作 AI
Redis 容器 lyread-redis (127.0.0.1:6379) — 当前后端未使用
APScheduler 后台任务：每 EVOLUTION_INTERVAL_SECONDS 执行一次自进化周期
```

## 后端

源码：`lyread/backend`。镜像通过 `docker build` 构建。

关键环境变量（通过 `--env-file` 注入，勿写入镜像）：

| 变量 | 说明 |
|------|------|
| `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` | 数据库连接 |
| `JWT_SECRET` (>=32 chars) / `JWT_EXPIRE_MINUTES` | 登录令牌 |
| `ALLOWED_ORIGINS` | CORS 白名单 |
| `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` | 创作 AI（缺失时回退 Pollinations 免费接口） |
| `AUTO_EVOLUTION` | `1` 启动时自动开启调度器（默认开） |
| `EVOLUTION_INTERVAL_SECONDS` | 自进化周期间隔（默认 900s） |
| `ADMIN_USERNAMES` | 管理员用户名白名单（逗号分隔） |
| `MAX_CONCURRENT_JOBS` | 单用户并发生成上限（默认 2） |
| `ALIPAY_*` | 支付宝收款（见 IMPLEMENTATION-STATUS.md） |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM` | 邮件发送（找回密码等） |
| `SITE_URL` | 站点根 URL，用于邮件中的重置链接 |
| `CONTENT_BLOCKLIST` | 敏感词扩展（逗号分隔） |
| `CONTENT_BLOCKLIST_FILE` | 敏感词文件路径（默认镜像内 `data/blocklist.txt`） |
| `EXPOSE_RESET_TOKEN` | 无 SMTP 时 `forgot` 接口返回令牌（`1` 开启） |

### 重新部署后端

```bash
cd /home/ubuntu/lyread-fix-build   # 服务器上的构建目录
docker build -t lyread-backend:fix-$(date +%Y%m%d-%H%M%S) .
# 停旧容器 → run 新容器（127.0.0.1:8004, --env-file /tmp/lyread.env, network lyread-net）
# 健康检查 /health/live，失败则回滚到上一个镜像 tag
```

回滚镜像 tag 形如 `lyread-backend:rollback-YYYYMMDD-HHMMSS`。

## 前端

源码：`lyread/frontend`（Vue3 + Vite）。

```bash
cd /home/ubuntu/lyread-v1.9/frontend
npm run build            # 产物在 dist/
sudo cp -r dist/* /usr/share/nginx/html/
sudo systemctl reload nginx
```

## 数据库

- 备份：`/home/ubuntu/backups/lyread-db-*.sql`（`mysqldump`）。
- 迁移：`lyread/backend/migrations/001_stories_user_id.sql`（为 `stories` 增加 `user_id`、`word_count`）。

## 安全加固

- MySQL/Redis 端口改为仅 `127.0.0.1` 监听（重建容器时用 `-p 127.0.0.1:3306:3306`）。
- 旧后端容器 `lyread-backend`(8003) 已停止并关闭自启。
- iptables 备份保存在 `/etc/iptables/rules.v4`（建议安装 `iptables-persistent` 以便开机恢复）。
- 建议后续：为 Redis 设置 `requirepass`、轮换 MySQL root 密码、将 `google-sa.json` 等密钥移出镜像。

## 监控

cron 看门狗（每 5 分钟）：`/health/live` 异常时自动 `docker restart lyread-backend-fix`，日志 `/var/log/lyread_watchdog.log`。

## 验收冒烟

```bash
BASE_URL=https://lyread.cn bash lyread/scripts/smoke_test.sh
```

覆盖：健康检查、注册、余额、创建作品、鉴权、敏感词拦截、管理员权限、找回密码。
