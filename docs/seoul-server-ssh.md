# 首尔服务器 SSH 部署指南

| 项目 | 值 |
|------|-----|
| 名称 | 首尔节点（12号服务器） |
| 公网 IP | `43.128.145.79` |
| 内网 IP | `10.60.0.2`（WireGuard） |
| 区域 | 腾讯云 · 首尔（ap-northeast-2） |
| 用户 | `ubuntu`（✅ 已验证） |
| 主机名 | `VM-0-5-ubuntu` |

## 公钥（添加到服务器）

将下面整行追加到服务器的 `~/.ssh/authorized_keys`：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP704MUNbh0EwfiIW9ZA8Gdqr6qOhmQV3Nkaioe9aNnV seoul-deploy-43.128.145.79
```

## 方法一：腾讯云网页终端（无需现有 SSH）

1. 打开 [腾讯云轻量服务器控制台](https://console.cloud.tencent.com/lighthouse/instance)
2. 找到 IP 为 `43.128.145.79` 的实例
3. 点击 **登录** → 使用网页终端
4. 执行：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP704MUNbh0EwfiIW9ZA8Gdqr6qOhmQV3Nkaioe9aNnV seoul-deploy-43.128.145.79' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 方法二：已有密码登录时

```bash
ssh ubuntu@43.128.145.79
# 登录后执行上面的 mkdir / echo / chmod 命令
```

## 本地连接（部署公钥后）

将私钥保存为 `~/.ssh/seoul_deploy`，然后：

```bash
chmod 600 ~/.ssh/seoul_deploy
ssh -i ~/.ssh/seoul_deploy ubuntu@43.128.145.79
```

## 验证

```bash
ssh -i ~/.ssh/seoul_deploy ubuntu@43.128.145.79 "hostname && uptime"
```

---

## 服务器探测报告（2026-07-19）

### 连通性

| 项目 | 状态 |
|------|------|
| Ping | ✅ 可达（~190ms） |
| SSH (22) | ✅ 开放（仅公钥认证） |
| HTTP (80) | ✅ 开放 → 301 跳转 HTTPS |
| HTTPS (443) | ✅ 开放 |

### 开放端口

| 端口 | 状态 | 备注 |
|------|------|------|
| 22 | ✅ 开放 | SSH |
| 80 | ✅ 开放 | nginx |
| 443 | ✅ 开放 | nginx + SSL |
| 3000 | ✅ 开放 | Next.js（建议限制内网） |
| 3306 | ✅ 开放 | MySQL（**安全风险**） |
| 5432 | ✅ 开放 | PostgreSQL（**安全风险**） |
| 6379 | ✅ 开放 | Redis（**安全风险**） |
| 8000 | ✅ 开放 | 应用服务 |
| 8080 | ✅ 开放 | 应用服务 |
| 8088 | ✅ 开放 | 应用服务（Virginia 边缘代理目标） |
| 8095 | ✅ 开放 | 应用服务 |

### SSL 证书

| 项目 | 值 |
|------|-----|
| 颁发机构 | Let's Encrypt (YE2) |
| 主域名 | zhenxi.hk.cn |
| SAN | zhenxi.hk.cn, www.zhenxi.hk.cn, g.zhenxi.hk.cn |
| 有效期 | 2026-07-04 ~ 2026-10-02 |

### 托管站点

| 域名 | DNS 指向 | 技术栈 | TTFB |
|------|----------|--------|------|
| zhenxi.hk.cn | 43.128.145.79 | Next.js + nginx | ~0.98s |
| cosgo.cn | 43.128.145.79 | Next.js + nginx | ~1.24s |
| cloudai-box.com | 43.128.145.79 | nginx 反代 | — |
| greentrace.com.cn | 43.128.145.79 | nginx 反代 | — |
| www.zhenxi.hk.cn | 43.152.241.132 | 曼谷边缘节点 | — |
| g.zhenxi.hk.cn | 43.172.29.127 | 弗吉尼亚边缘节点 | — |

### 多区域架构

```
首尔后端 (43.128.145.79 / 10.60.0.2)
├── zhenxi.hk.cn      ← 主站 Next.js
├── cosgo.cn          ← Next.js
├── cloudai-box.com
└── greentrace.com.cn

弗吉尼亚边缘 (43.172.29.127)
├── g.zhenxi.hk.cn    ← /seo/ 代理回首尔
├── getnudex.com
├── attyflow.com
├── yoko.hk.cn
└── tianshu.online

曼谷边缘 (43.152.241.132)
├── momei.ink
├── siamsaas.com
└── www.zhenxi.hk.cn  ← 边缘代理
```

WireGuard 内网：`10.60.0.2`（首尔）↔ `10.60.0.3`（追踪）↔ `10.60.0.5`（曼谷）

### 安全建议（P0）

1. **MySQL (3306)、PostgreSQL (5432)、Redis (6379)** 应对外关闭，仅允许 `127.0.0.1` 或 WireGuard 内网访问
2. **Next.js (3003–3006)** 绑定 `0.0.0.0`，应改为 `127.0.0.1`，仅通过 nginx 反代
3. 部署 SSH 公钥后，建议禁用密码登录

---

## SSH 深度审计（2026-07-19）

### 系统状态

| 项目 | 值 |
|------|-----|
| 主机名 | `VM-0-5-ubuntu` |
| 系统 | Ubuntu, Linux 6.8.0-117 |
| 运行时间 | 42 天 |
| 内存 | 3.6G 总量，1.7G 已用，Swap 1.9G 已用 |
| 磁盘 | 59G 总量，**73% 已用**（已从 97% 清理） |
| 负载 | 1.54 |

### 已执行修复

| 操作 | 效果 |
|------|------|
| 清理 `/root/.pm2/logs`（9.3G） | 磁盘 97% → **73%**，释放 ~14G |
| `npm cache clean` | 清理 root npm 缓存 |
| `journalctl --vacuum-size=100M` | 压缩系统日志 |

### 运行服务

| 服务 | 端口 | 状态 |
|------|------|------|
| nginx (公网) | 80, 443 | ✅ active |
| nginx-backend | 8088 | ✅ active（边缘代理入口） |
| zhenxi (Next.js) | 3005 | ✅ active |
| cosgo (Next.js) | 3004 | ✅ active |
| after2am (Next.js) | 3003, 3006 | ✅ active |
| after2am-api (PM2) | 8091 | ✅ online |
| cloudai API (Docker) | 127.0.0.1:8001 | ✅ healthy |
| APISIX Edge (Docker) | 8080, 9443 | ✅ Up 3 weeks |
| MySQL | 127.0.0.1:3306 | ✅ localhost only |
| PostgreSQL | 127.0.0.1 + 10.60.0.2 | ✅ 内网 |
| Redis | 127.0.0.1 + 10.60.0.2 | ✅ 内网 |
| v2ray | 10086, 10808 | ✅ 代理服务 |

### 站点健康

| 站点 | HTTP 状态 |
|------|-----------|
| zhenxi.hk.cn | ✅ 200 |
| cosgo.cn | ✅ 200 |
| cloudai-box.com | ✅ 200 |
| greentrace.com.cn | ✅ 200 |

### WireGuard 拓扑

| Peer | 公网 IP | 内网 IP | 握手 |
|------|---------|---------|------|
| 上海A | 150.158.42.39 | 10.60.0.3 | 18s ago |
| 弗吉尼亚 | 43.172.29.127 | 10.60.0.1 | 1m47s ago |
| 曼谷 | 43.152.241.132 | 10.60.0.5 | 1m54s ago |
| 其他 | 43.157.175.48 | 10.60.0.4 | 36s ago |

首尔本机：`10.60.0.2`，监听端口 443

### 部署目录

| 路径 | 大小 | 用途 |
|------|------|------|
| `/opt/zhenxi` | 1.0G | zhenxi.hk.cn 主站 |
| `/opt/cosgo` | 1.2G | cosgo.cn |
| `/opt/greentrace` | 273M | greentrace.com.cn |
| `/opt/cloudai-box` | 122M | cloudai-box.com |
| `/opt/umami` | 1.4G | 分析服务 |
| `/data/www` | 7.1G | after2am 等站点数据 |

### 待优化（P1–P2）

| 优先级 | 项目 | 说明 |
|--------|------|------|
| P1 | PM2 日志轮转 | 配置 `pm2-logrotate`，防止再次撑满磁盘 |
| P1 | Next.js 端口内网化 | 3003–3006 改为 `127.0.0.1` |
| P1 | `/home/ubuntu/.hermes` (3.1G) | 评估是否可清理或迁移 |
| P2 | Swap 使用率高 (1.9G/3.9G) | 考虑升级内存或优化进程 |
| P2 | zhenxi/cosgo 站点优化 | ✅ 已执行（见下方） |

---

## 优化执行记录（2026-07-19）

### P1 安全加固

| 服务 | 端口 | 绑定 |
|------|------|------|
| zhenxi | 3005 | ✅ 127.0.0.1 |
| cosgo | 3004 | ✅ 127.0.0.1 |
| after2am | 3003 | ⚠️ 仍监听 `*:3003`（非主站，待处理） |

### zhenxi.hk.cn 增长优化

- ✅ 首页新增「最新疗愈文章」区块（3 篇精选）
- ✅ 底部 CTA 双按钮：测评 + 浏览文章
- ✅ 重建 Next.js 并启用 systemd 自启（`zhenxi.service`）
- ✅ IndexNow 提交量 10 → 50 URLs

### cosgo.cn 增长优化

- ✅ 首页 `force-dynamic` → `revalidate: 3600`（ISR 缓存，降低 TTFB）
- ✅ 最新攻略展示 3 → 6 篇
- ✅ 新增「漫展季」顶部横幅 → `/activities`
- ✅ IndexNow 批量提交

---

## P0 SEO 修复（2026-07-19）

针对增长诊断中的 P0 问题，已在服务器 `/opt/zhenxi` 执行：

| 问题 | 修复 | 验证 |
|------|------|------|
| `sitemap.xml` 404 | `start.sh` 增加 `public` 符号链接；nginx 直出兜底 | ✅ HTTP 200 |
| `og-image.png` 404 | 同上 | ✅ HTTP 200 |
| 全站 canonical 指向首页 | 移除 `layout.tsx` 全局 canonical；各路由独立设置 | ✅ `/blog` → `/blog` |
| `/en` hreflang 404 | 移除无效 `en` 语言 alternate | ✅ 无 `/en` 引用 |
| SearchAction → `/search` 404 | 移除 JSON-LD SearchAction | ✅ 无 SearchAction |
| `logo.png` 404 | Schema.org logo 改为 `og-image.png` | ✅ |

### 变更文件（服务器）

- `/opt/zhenxi/start.sh` — 增加 `public` symlink
- `/opt/zhenxi/src/lib/seo.ts` — `pageCanonical()` 辅助函数
- `/opt/zhenxi/src/app/layout.tsx` — 移除全局 canonical、en hreflang、SearchAction
- `/opt/zhenxi/src/app/*/page.tsx` — 各页面独立 canonical
- `/opt/zhenxi/src/app/contact/layout.tsx` — 联系页 metadata（client 组件分离）
- `/etc/nginx/sites-enabled/traffic-override.conf` — sitemap/og-image 直出

### 部署脚本

```bash
scp scripts/zhenxi-p0-seo.py ubuntu@43.128.145.79:/tmp/
ssh ubuntu@43.128.145.79 'python3 /tmp/zhenxi-p0-seo.py'
```

### 验证命令

```bash
curl -sI https://zhenxi.hk.cn/sitemap.xml | head -1
curl -sI https://zhenxi.hk.cn/og-image.png | head -1
curl -s https://zhenxi.hk.cn/blog | grep canonical
```

---

## P2 性能优化（2026-07-19）

| 项目 | 动作 | 状态 |
|------|------|------|
| Swap 缓解 | `vm.swappiness` 50 → 10（持久化 `/etc/sysctl.d/99-seoul-tuning.conf`） | ✅ |
| PM2 冲突 | 删除 root PM2 中指向 `/data/www/cosgo` 的 crash-loop cosgo（systemd 已管理） | ✅ |
| zhenxi 静态缓存 | nginx 增加 `/_next/static/` 1年 immutable + 图片 7天缓存 | ✅ |
| zhenxi HTML 缓存 | `max-age=3600` → `s-maxage=3600, stale-while-revalidate=86400` | ✅ |
| 30 天内容计划 | 见 `docs/zhenxi-content-plan-30d.md` | ✅ 文档 |
| P3 路线图 | 见 `docs/growth-roadmap-p3.md` | ✅ 文档 |

### 部署脚本

```bash
scp scripts/seoul-p2-optimize.py ubuntu@43.128.145.79:/tmp/
ssh ubuntu@43.128.145.79 'python3 /tmp/seoul-p2-optimize.py'
```

### 已知限制（移交 P3）

- Swap 仍 ~2.1G（Hermes agent + MySQL 为主要占用；需升配或迁出 Hermes）
- Cloudflare CDN 需 DNS 权限
- 邮件收集 / 付费测评需第三方服务接入
