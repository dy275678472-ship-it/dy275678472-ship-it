# LyRead 服务器 SSH 部署指南

> 与上海A、曼谷等服务器使用**同一套模式**：Cloud Agent 生成密钥对 → 您把**公钥**写入服务器 → Agent 即可远程部署。

| 项目 | 值 |
|------|-----|
| 名称 | LyRead 生产机 |
| IP | `101.34.63.137` |
| 域名 | `lyread.cn` |
| 用户 | `ubuntu`（已验证可用） |
| 密钥备注 | `cursor-cloud-agent-lyread` |

## 公钥（添加到服务器）

将下面整行追加到服务器的 `~/.ssh/authorized_keys`：

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMib+pZDf5FI8wXz3kWkW4ShjgO7kkAb3henqokembdw cursor-cloud-agent-lyread
```

指纹：`SHA256:vmaJqvlHBxOtMxAAchrNreGZ84xy2SR3hDzcO87lbxo`

## 方法一：腾讯云网页终端（推荐，无需现有 SSH）

1. 打开 [腾讯云轻量服务器控制台](https://console.cloud.tencent.com/lighthouse/instance)
2. 找到 IP 为 `101.34.63.137` 的实例
3. 点击 **登录** → 使用网页终端
4. 执行：

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMib+pZDf5FI8wXz3kWkW4ShjgO7kkAb3henqokembdw cursor-cloud-agent-lyread' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 方法二：已有密码登录时

```bash
ssh ubuntu@101.34.63.137
# 登录后执行上面的 mkdir / echo / chmod 命令
```

## 验证（公钥写入后）

在任意已授权机器上：

```bash
ssh ubuntu@101.34.63.137 "hostname && whoami && uptime"
# 期望输出：VM-0-13-ubuntu / ubuntu / uptime...
```

Cloud Agent 侧使用私钥路径：`/home/ubuntu/.ssh/lyread_id`

## 与其他服务器的对比

| 服务器 | IP | 用户 | 公钥备注 |
|--------|-----|------|----------|
| 上海A | `150.158.42.39` | `ubuntu` | `shanghai-a-deploy-150.158.42.39` |
| LyRead | `101.34.63.137` | `ubuntu` | `cursor-cloud-agent-lyread` |
| 曼谷 | 见 SiamSaaS Agent | `ubuntu` | 各 Agent 独立密钥 |

**共同点：**
- 都用 `ubuntu` 用户（不用 `root`）
- 都把公钥写入 `~/.ssh/authorized_keys`
- 目录权限 `700`，文件权限 `600`
- 安全组需放行 **22 端口**（来源可限制为 Cursor Cloud 出口 IP，或临时 `0.0.0.0/0`）

## 公钥写入后 — 一键部署前端

```bash
cd ~
git clone https://github.com/dy275678472-ship-it/dy275678472-ship-it.git lyread-deploy 2>/dev/null || (cd lyread-deploy && git pull)
cd lyread-deploy && git checkout cursor/lyread-full-rewrite-bf92
cd lyread/frontend && npm install && npm run build
sudo cp -r dist/* /usr/share/nginx/html/
sudo systemctl reload nginx
```

## 公钥写入后 — 告诉 Cursor Agent

在 Cursor Cloud Agent 对话中说：

> 公钥已写入 101.34.63.137，请 SSH 部署

Agent 会使用 `ssh -i /home/ubuntu/.ssh/lyread_id ubuntu@101.34.63.137` 连接并执行部署。

## 服务器当前架构

```
nginx (443) → /usr/share/nginx/html  (Vue3 SPA)
           → 127.0.0.1:8004          (FastAPI 后端容器 lyread-backend-fix)
MySQL  lyread-mysql  (127.0.0.1:3306)
Redis  lyread-redis  (127.0.0.1:6379)
环境变量：/tmp/lyread.env
```

详细运维见 `lyread/DEPLOY.md`。
