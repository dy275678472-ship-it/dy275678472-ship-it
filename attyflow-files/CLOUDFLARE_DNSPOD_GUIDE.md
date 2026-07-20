# Cloudflare 接入指南 — DNSPod 切换 NS（attyflow.com）

> **当前状态：** DNS 在 **DNSPod**，A 记录指向源站 `43.172.29.127`，流量直连，无 CDN。  
> **目标状态：** 域名 NS 改为 Cloudflare，边缘 CDN + SSL + DDoS 防护，源站 nginx 已配置真实 IP 回源。

---

## 切换前检查清单

| 项目 | 命令 / 位置 | 预期 |
|------|-------------|------|
| 源站 HTTPS 正常 | `curl -sI https://attyflow.com/ \| head -5` | `HTTP/2 200` |
| Let's Encrypt 证书 | 服务器 `/etc/letsencrypt/live/attyflow.com/` | 证书未过期 |
| nginx Cloudflare 真实 IP | `/etc/nginx/conf.d/cloudflare-real-ip.conf` | 已 include |
| API 健康 | `curl -s http://127.0.0.1:8001/api/health` | `{"ok":true,...}` |
| 备份当前 DNSPod 记录 | DNSPod 控制台截图 | A / www / 邮件等 |

**预计生效时间：** 通常 5–30 分钟，最长 48 小时。  
**建议切换窗口：** 工作日白天（便于观察），PH 发布日可提前 24h 切换以稳定缓存。

---

## 第一步：在 Cloudflare 添加站点

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击 **Add a site** → 输入 `attyflow.com` → 选择 **Free** 计划
3. Cloudflare 自动扫描现有 DNS 记录，核对以下记录：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|----------|
| A | `@` | `43.172.29.127` | **Proxied（橙色云）** |
| A 或 CNAME | `www` | `43.172.29.127` 或 `attyflow.com` | **Proxied** |

4. 如有子域名（如 `api.`、`mail.`），按实际需要添加；**未列出的记录切换 NS 后会丢失**，务必在 Cloudflare 中补全。
5. 记录 Cloudflare 分配的两条 NS，例如：
   - `ada.ns.cloudflare.com`
   - `bob.ns.cloudflare.com`  
   （实际以控制台显示为准，不要使用本文示例域名。）

---

## 第二步：在 DNSPod 修改 NS（核心步骤）

### 路径（腾讯云 DNSPod）

1. 登录 [DNSPod 控制台](https://console.dnspod.cn/)
2. **域名解析** → 找到 `attyflow.com`
3. 进入域名详情 → **DNS 服务器** / **修改 DNS 服务器**
4. 将原有 DNSPod NS（常见为 `*.dnspod.net` 或 `*.dnspod.cn`）**全部替换**为 Cloudflare 提供的两条 NS
5. 保存

### 注意事项

- **只改 NS，不要同时改 A 记录。** NS 切换后，解析由 Cloudflare 管理。
- 若域名在 **腾讯云注册**，有时需在「域名注册 → 修改 DNS」与 DNSPod 两处一致。
- 切换期间可能出现短暂解析抖动（部分用户直连、部分走 CF），属正常现象。

### 验证 NS 是否生效

```bash
# 应返回 cloudflare.com 的 NS
dig NS attyflow.com +short

# 或
nslookup -type=NS attyflow.com
```

---

## 第三步：Cloudflare SSL/TLS 设置

进入 **SSL/TLS** → **Overview**：

| 设置项 | 推荐值 | 说明 |
|--------|--------|------|
| **SSL/TLS encryption mode** | **Full (strict)** | 源站已有有效 LE 证书，必须 strict |
| Always Use HTTPS | **On** | 强制 HTTPS |
| Automatic HTTPS Rewrites | **On** | 修复混合内容 |
| Minimum TLS Version | **TLS 1.2** | 合规默认值 |

**切勿使用 Flexible**（仅边缘 HTTPS、回源 HTTP）—— 源站已配置 HTTPS，Flexible 会导致重定向循环或安全降级。

验证证书：

```bash
curl -sI https://attyflow.com/ | grep -iE 'cf-ray|server|HTTP'
# 期望看到 cf-ray: ... 和 server: cloudflare
```

SSL 实验室检测（可选）：  
https://www.ssllabs.com/ssltest/analyze.html?d=attyflow.com

---

## 第四步：缓存规则（Free 可用 Cache Rules）

**Caching → Cache Rules → Create rule**

### 规则 1 — 静态资源长缓存

- **If:** URI Path starts with `/assets/`
- **Then:** Cache eligibility = Eligible for cache · Edge TTL = 7 days · Browser TTL = 1 day

### 规则 2 — WebP / 图片

- **If:** URI Path ends with `.webp` OR equals `/og-image.png`
- **Then:** Edge TTL = 7 days（og-image 可用 1 day）

### 规则 3 — 动态内容绕过

- **If:** URI Path starts with `/api/` OR equals `/taskpane.html`
- **Then:** Cache eligibility = **Bypass cache**

### 规则 4 — HTML 页面（可选，保守）

- **If:** URI Path ends with `.html` OR equals `/`
- **Then:** Edge TTL = 2 hours（或 Bypass，若需即时更新首页 banner）

**Speed → Optimization：** 开启 Brotli、Auto Minify（JS/CSS/HTML 按需）。

---

## 第五步：安全与性能（推荐）

| 模块 | 设置 |
|------|------|
| **Security → Settings** | Security Level = Medium；Bot Fight Mode = On（可选） |
| **Speed → Early Hints** | On |
| **Network** | HTTP/2、HTTP/3 (QUIC) = On |
| **Scrape Shield** | Hotlink Protection 按需（一般 Off，避免误伤） |

**Page Rules（若仍使用旧版）：** 免费计划限 3 条，优先 `/assets/*` Cache Everything、`/api/*` Bypass。

---

## 第六步：切换后验证（必做）

在**本地终端**和**服务器**各执行：

```bash
# 1. Cloudflare 已代理
curl -sI https://attyflow.com/ | grep -i cf-ray
# 有 cf-ray 即成功

# 2. 首页与 launch 页
curl -sI https://attyflow.com/launch/ | head -3
curl -sI https://attyflow.com/taskpane.html | head -3

# 3. API 不被缓存（应 Bypass）
curl -sI https://attyflow.com/api/health | grep -iE 'cf-cache-status|HTTP'
# cf-cache-status: DYNAMIC 或 BYPASS 为正常

# 4. 源站真实 IP 日志（SSH 到服务器）
sudo tail -20 /var/log/nginx/access.log
# 应看到真实访客 IP，而非仅 Cloudflare IP 段

# 5. PH 监控脚本
sudo python3 /var/www/attyflow/tools/attyflow_ph_monitor.py
```

**浏览器检查：** 打开 DevTools → Network → 响应头应含 `cf-ray`、`server: cloudflare`。

---

## 第七步：Search Console / 第三方

1. **Google Search Console：** 域名已在 GSC 验证则通常无需重验；若用 URL 前缀验证，切换后确认 HTTPS 属性正常。
2. **IndexNow / Bing：** 无需改 key，URL 不变。
3. **Stripe / Webhook：** 若回调 URL 为 `https://attyflow.com/api/...`，切换 CF 后一般无影响；若有 IP 白名单需改为 Cloudflare IP 或关闭 IP 限制。

---

## 回滚方案（紧急）

若切换后出现 525/526 SSL 错误或全站不可访问：

1. **DNSPod** → 将 NS **改回**原 DNSPod 服务器（如 `raspberry.dnspod.net` / `setting.dnspod.net`，以你账户历史为准）
2. 在 DNSPod **域名解析** 中确认 A 记录 `@` → `43.172.29.127` 仍在
3. 等待 5–30 分钟传播
4. 验证：`curl -sI https://attyflow.com/` 应恢复直连（无 `cf-ray`）

源站 nginx 的 `cloudflare-real-ip.conf` **可保留**——无 CF 头时不影响直连访问。

---

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| **525 SSL handshake failed** | CF 与源站 SSL 不匹配 | 确认 CF 模式为 Full (strict)；检查 LE 证书是否过期 |
| **526 Invalid SSL certificate** | 源站证书域名不匹配或自签 | 续期 `certbot renew`；确保证书含 `attyflow.com` |
| **521 Web server is down** | 源站 nginx/防火墙未响应 | SSH 检查 `sudo nginx -t && sudo systemctl reload nginx` |
| **重定向过多** | Flexible + 源站强制 HTTPS | 改为 Full (strict) |
| **API 返回旧数据** | `/api/*` 被缓存 | 添加 Bypass 规则并 Purge Cache |
| **看不到 cf-ray** | NS 未生效或本地 DNS 缓存 | `dig NS attyflow.com`；换网络或 `1.1.1.1` 再测 |

---

## 相关文件（服务器）

| 路径 | 说明 |
|------|------|
| `/etc/nginx/conf.d/cloudflare-real-ip.conf` | Cloudflare IP 段 + `CF-Connecting-IP` |
| `/etc/nginx/sites-enabled/traffic-override.conf` | attyflow 站点配置 |
| `/var/www/attyflow/CLOUDFLARE_SETUP.md` | 英文简要版 |
| `/var/www/attyflow/tools/attyflow_ph_monitor.py` | PH 发布日监控 |

---

## 操作记录模板（建议填写）

```
切换日期：____年__月__日 __:__ UTC
操作人：________
Cloudflare NS：________________ / ________________
切换前 dig NS：________________
切换后 dig NS：________________
cf-ray 首次出现时间：____:__
SSL 模式：Full (strict) ✓
缓存规则已创建：是 / 否
回滚测试：未测 / 已测
备注：________________
```

---

**完成后：** 在 PH 发布日运行 `sudo python3 /var/www/attyflow/tools/attyflow_ph_monitor.py --watch 300` 观察流量与转化。  
**Launch 运营文案：** `/launch/playbook/` 或 `launch/SOCIAL_LAUNCH_COPY.md`
