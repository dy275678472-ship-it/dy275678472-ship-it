# 08 · Prompt 版本化规范

## 目标

- Prompt 与代码解耦，可迭代、可回滚、可 A/B。
- 每次生成记录使用的 `prompt_version`（写入 `generation_jobs`），便于对比效果与成本。

## 存放方式

- 目录 `backend/prompts/<job_type>/<version>.txt`（如 `chapter/v3.txt`）。
- 或表 `prompt_templates(job_type, version, content, is_active, created_at)`，运行期按 `job_type` 取 `is_active` 版本。
- 变量用 `{{name}}` 占位，代码渲染时替换。

## 各任务 Prompt 要点

- **title**：核心元素 + 题材 → 输出 5 行「书名 | 一句话钩子」。
- **outline**：书名/简介/题材/爽点 → 起承转合 JSON。
- **chapters**：宏观大纲 + 章数 → 每章 `{chapter,title,hot_point,summary}` JSON 数组。
- **chapter**（正文）：作品设定 + 记忆快照 + 人物状态 + 未回收伏笔 + 最近摘要 + 最近正文 + 本章章纲 → 约 2000 字正文。
- **continue**：同上，强调风格一致与衔接。
- **summary**（记忆）：输入本章正文 → 输出压缩摘要 + 人物状态变化 + 新增/回收伏笔（结构化 JSON，供记忆子流程解析）。
- **consistency**：输入记忆 + 本章 → 输出冲突列表。

## 硬约束

- 结构化输出（JSON）必须给出严格 schema 并在代码侧用正则/`json.loads` 容错解析（失败重试或降级）。
- Prompt 内不得含真实密钥、用户隐私。
- 版本切换必须可回滚（保留旧版本文件/记录）。
