# 上海A 服务器 SSH 部署指南

| 项目 | 值 |
|------|-----|
| 名称 | 上海A |
| IP | `150.158.42.39` |
| 区域 | 腾讯云 · 上海 |
| 用户 | `root`（如无法登录可试 `ubuntu`） |

## 公钥（添加到服务器）

将下面整行追加到服务器的 `~/.ssh/authorized_keys`：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICYlMSw/P0ur4hFyLv0mklVR383HpHMHvjeVUQS+t8xP shanghai-a-deploy-150.158.42.39
```

## 方法一：腾讯云网页终端（无需现有 SSH）

1. 打开 [腾讯云轻量服务器控制台](https://console.cloud.tencent.com/lighthouse/instance)
2. 找到 IP 为 `150.158.42.39` 的实例
3. 点击 **登录** → 使用网页终端
4. 执行：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICYlMSw/P0ur4hFyLv0mklVR383HpHMHvjeVUQS+t8xP shanghai-a-deploy-150.158.42.39' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 方法二：已有密码登录时

```bash
ssh root@150.158.42.39
# 登录后执行上面的 mkdir / echo / chmod 命令
```

## 本地连接（部署公钥后）

将私钥保存为 `~/.ssh/shanghai_a_deploy`，然后：

```bash
chmod 600 ~/.ssh/shanghai_a_deploy
ssh -i ~/.ssh/shanghai_a_deploy root@150.158.42.39
```

## 验证

```bash
ssh -i ~/.ssh/shanghai_a_deploy root@150.158.42.39 "hostname && uptime"
```

## 服务器当前状态（2026-07-18）

- nginx/1.24.0 + Next.js（CosGo 等站点）
- 开放端口：22, 80, 443, 8080, 3306, 6379
- 建议：将 MySQL(3306)、Redis(6379) 限制为内网访问
