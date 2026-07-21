# Esylink — 易连云通信持续优化

[esylink.cn](https://esylink.cn) 的源码管理、部署脚本与运维工具。

## 快速开始

```bash
# 1. 健康检查（无需 SSH）
python3 esylink/scripts/health_check.py

# 2. SSH 公钥写入服务器后（见 docs/esylink-ssh.md）
bash esylink/scripts/deploy.sh
```

## 文档

- [SSH 部署指南](../docs/esylink-ssh.md)
- [运维审计报告](../docs/esylink-ops-audit.md)

## 本次优化（2026-07-18）

- 扩展 `page-track.js` CTA 追踪：覆盖 `/dialer/`、`tel:`、企微登录
- 扩展 `esylink-chat.js` 高意图页面判定
- 新增 `optimize-pages.py`：为缺埋点的产品页批量注入脚本
- 修正首页 OG 标题与页面标题不一致
- 新增健康检查 + 一键部署脚本
