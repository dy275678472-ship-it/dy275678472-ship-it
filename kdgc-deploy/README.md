# KDGC 全栈部署包

上海A服务器 `150.158.42.39` 上的中科国瓷官网全栈重构。

## 已部署（2026-07-18）

### Phase 0 ✅
- nginx 直出静态文件（停用 python http.server）
- 3000 端口已关闭
- 后端绑定 127.0.0.1:8000
- 备份：`/opt/kdgc-growth.backup.20260718`

### Phase 1 ✅
- 多页面静态站点 `/opt/kdgc-growth/frontend/dist/`
- FastAPI v2 后端 `/opt/kdgc-growth/backend/`
- PostgreSQL 种子数据（3 产品 / 5 新闻 / 2 案例）
- 真实 CRM `/api/leads`（已验证写入）
- robots.txt + sitemap.xml
- 图片 WebP 优化

### Phase 2 ✅
- 案例页、新闻页、关于页、知识库
- Schema.org、SEO meta
- 管理后台 `/admin/`（Token 鉴权）

### Phase 3 ✅（骨架）
- 英文首页 `/en/`
- AI 材料助手 `/api/ai/chat` + 页面浮窗
- 管理后台线索列表

## 待完成（需人工）

| 项目 | 说明 |
|------|------|
| DNS | `kdgc.cc` A 记录 → `150.158.42.39` |
| SSL | DNS 生效后：`sudo certbot --nginx -d kdgc.cc -d www.kdgc.cc` |
| ICP 备案号 | 页脚占位 `[待公司提供]` |
| 飞书通知 | 设置 `FEISHU_WEBHOOK` 环境变量 |
| 公司资料 | 电话、地址、证书、专家照片 |

## 访问方式

域名未绑定前，直接用 IP（HTTP / HTTPS 均可）：

- http://150.158.42.39/
- https://150.158.42.39/ （自签证书，浏览器会提示不安全，点继续即可）

```bash
# SSH
ssh -i ~/.ssh/shanghai_a_deploy ubuntu@150.158.42.39
```

说明：nginx 已将本站设为 80/443 的 `default_server`，避免 IP 访问落到 cosgo 死上游导致 502。

## 重新部署

```bash
cd /opt/kdgc-growth && bash deploy/install.sh
```

## 管理后台

- URL: `http://kdgc.cc/admin/`（DNS 生效后）
- Token: 见 `/etc/systemd/system/kdgc-backend.service` 中 `ADMIN_TOKEN`
