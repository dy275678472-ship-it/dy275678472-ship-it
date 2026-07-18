# LyRead V2 实施状态

最后更新：2026-07-18（第三阶段）

## 已完成

### 第一阶段 P0
注册/登录、点数计费、创作台、价格/钱包、案例阅读、导出、沙箱充值

### 第二阶段
运营后台、内容审核、一致性检测、并发限制、支付宝 RSA2

### 第三阶段（本次）
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

## 待完成（P2）

| 模块 | 说明 |
|------|------|
| 支付宝商户密钥 | 配置后即可正式收款 |
| 邮件发送重置链接 | 当前 `EXPOSE_RESET_TOKEN=1` 返回令牌 |
| SMTP 通知 | 可选 |
| story_projects 表迁移 | 当前沿用 `stories` 表 |

## 环境变量

```bash
EXPOSE_RESET_TOKEN=1   # 无邮件时允许 forgot 接口返回重置令牌
ADMIN_USERNAMES=user001
ALIPAY_APP_ID=...
```

## 核心链路

> 创作 → 续写（自动更新大脑）→ 章节入库 → 提交审核 → 后台通过 → 案例区
