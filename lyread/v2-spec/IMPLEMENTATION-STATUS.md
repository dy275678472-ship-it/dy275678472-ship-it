# LyRead V2 实施状态

最后更新：2026-07-18（第二阶段）

## 已完成

### P0 核心
- 注册/登录、点数计费、创作台、价格/钱包、案例阅读、导出、小说大脑基础、沙箱充值

### 第二阶段新增
| 模块 | 状态 |
|------|------|
| 运营后台 `/api/admin` + `/admin` 页面 | ✅ |
| 内容审核队列 `content_reviews` | ✅ |
| 发布走审核（通过后进案例区） | ✅ |
| 管理员额度调整 `admin_adjust` | ✅ |
| 一致性检测 API `/consistency-check` | ✅ |
| 并发任务限制 429 | ✅ |
| 支付宝 RSA2 签名 + 支付 URL 生成 | ✅（需配置密钥） |
| 支付宝回调验签 | ✅ |

## 待完成（P1/P2）

| 模块 | 说明 |
|------|------|
| 支付宝商户密钥 | 配置 `ALIPAY_APP_ID` / `ALIPAY_PRIVATE_KEY` / `ALIPAY_PUBLIC_KEY` |
| 章节独立表 `chapters` | 仍用 JSON，功能可用 |
| 找回密码 | V2.1 |
| 完整小说大脑 | 人物/伏笔/设定分表 |

## 管理员配置

在服务器 `/tmp/lyread.env` 添加：

```bash
# 方式一：用户名白名单（逗号分隔）
ADMIN_USERNAMES=你的用户名

# 方式二：数据库
# UPDATE users SET role='admin' WHERE username='你的用户名';

# 支付宝（正式收款）
ALIPAY_APP_ID=
ALIPAY_PRIVATE_KEY=
ALIPAY_PUBLIC_KEY=
ALIPAY_NOTIFY_URL=https://lyread.cn/api/orders/alipay/notify
ALIPAY_RETURN_URL=https://lyread.cn/wallet
ALIPAY_SANDBOX=0

MAX_CONCURRENT_JOBS=2
```

## 验收链路

> 创作 → 提交审核 → 管理员通过 → 案例区展示 → 用户充值（沙箱/支付宝）
