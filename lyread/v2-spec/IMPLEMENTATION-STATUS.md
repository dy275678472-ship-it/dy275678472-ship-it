# LyRead V2 实施状态

最后更新：2026-07-18（第四阶段）

## 已完成

### 第一阶段 P0
注册/登录、点数计费、创作台、价格/钱包、案例阅读、导出、沙箱充值

### 第二阶段
运营后台、内容审核、一致性检测、并发限制、支付宝 RSA2

### 第三阶段
| 模块 | 状态 |
|------|------|
| `chapters` 独立表 | ✅ 保存/续写同步写入 |
| 小说大脑完整表 | ✅ characters / world_settings / foreshadowings |
| 续写自动更新大脑 | ✅ LLM 提取摘要/人物/伏笔/设定 |
| 章节列表 API | ✅ `GET /api/story/{id}/chapters` |
| 大脑完整视图 | ✅ `GET /api/story/{id}/memory` |
| 找回密码 | ✅ `/api/auth/forgot` + `/reset` |
| 创作台章节列表 + 大脑面板 | ✅ |
| 登录页忘记密码流程 | ✅ |

### 第四阶段（本次）
| 模块 | 状态 |
|------|------|
| SMTP 邮件发送 | ✅ `services/email.py`，配置后自动发重置链接 |
| 内容安全（敏感词） | ✅ 生成前后检测 + 发布/审核拦截 |
| 验收冒烟脚本 | ✅ `lyread/scripts/smoke_test.sh` |

## 待完成（P2）

| 模块 | 说明 |
|------|------|
| 支付宝商户密钥 | 配置后即可正式收款 |
| SMTP 凭据 | 配置 `SMTP_HOST` 等后邮件自动发送 |
| `story_projects` 表迁移 | 当前沿用 `stories` 表 |
| token 成本记录 | generation_jobs 字段已有，待写入 |

## 环境变量

```bash
# 邮件（第四阶段）
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=noreply@lyread.cn
SMTP_TLS=1
SITE_URL=https://lyread.cn

# 内容安全
CONTENT_BLOCKLIST=额外词1,额外词2
CONTENT_BLOCKLIST_FILE=/app/data/blocklist.txt

# 密码重置（无邮件时）
EXPOSE_RESET_TOKEN=1

ADMIN_USERNAMES=user001
ALIPAY_APP_ID=...
```

## 验收

```bash
BASE_URL=https://lyread.cn bash lyread/scripts/smoke_test.sh
```

## 核心链路

> 创作 → 续写（自动更新大脑）→ 章节入库 → 提交审核 → 后台通过 → 案例区
