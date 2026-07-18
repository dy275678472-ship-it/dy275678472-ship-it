# LyRead V2 实施状态

最后更新：2026-07-18

## 已完成（P0）

| 模块 | 状态 | 说明 |
|------|------|------|
| 注册/登录 | ✅ | bcrypt + JWT，12 位用户 ID，注册送 30 点 |
| 点数账户 | ✅ | free/paid 分账，reserve/settle/refund |
| 每日免费额度 | ✅ | `/api/credits/daily-claim`，每日 5 点 |
| 生成扣费 | ✅ | 书名/大纲/章纲/续写均已接入 |
| 作品 CRUD | ✅ | save/list/get/update/delete，用户隔离 |
| 创作台前端 | ✅ | `/workspace` 完整流程 |
| 价格/钱包页 | ✅ | `/pricing` `/wallet` |
| 案例阅读 | ✅ | `/api/cases` + `/trending` |
| 导出 | ✅ | `/api/story/{id}/export?format=txt\|md` |
| 小说大脑（基础） | ✅ | `chapter_summaries` + 续写上下文 + 摘要自动更新 |
| 订单/充值骨架 | ✅ | 创建订单 + 沙箱确认 + 支付宝回调骨架 |
| 进化调度器 | ✅ | APScheduler 真实周期任务 |
| SSH 部署文档 | ✅ | `docs/lyread-ssh.md` |
| 前端已部署 | ✅ | lyread.cn |

## 部分完成 / 待加强

| 模块 | 状态 | 缺口 |
|------|------|------|
| 支付宝正式支付 | 🟡 | 需配置 `ALIPAY_APP_ID` / 公私钥；沙箱可用 |
| 章节独立表 | 🟡 | 仍用 `stories.chapters` JSON；`chapters` 表未迁移 |
| 一致性检测 API | 🟡 | 价目有 `consistency:2`，独立接口待补 |
| 内容审核队列 | 🟡 | `content_reviews` 表未建 |
| 运营后台 | ❌ | `/api/admin` 未实现 |
| 找回密码 | ❌ | V2.1 |
| 并发任务限制 | ❌ | 429 未实现 |
| IP 市场/全网分发 | ⏸️ | 已下线（V2 决定） |

## 环境变量（生产）

见 `lyread/DEPLOY.md`。支付额外需要：

```
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
ALIPAY_SANDBOX=1   # 测试时开启沙箱确认
```

## 验收对照

参见 `v2-spec/10-ACCEPTANCE-TESTS.md`。核心链路：

> 免费试写 → 注册 → 创作台生成大纲/章纲/续写 → 点数扣费 → 导出

该链路已可端到端走通（沙箱充值可用）。
