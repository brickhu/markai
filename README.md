# 📌 MarkAI — Capture every spark in your agent. AI that knows you.

> 🇨🇳 [中文版本](#-markai--capture-every-spark-in-your-agent-ai-that-knows-you-1)

A **local-first** personal knowledge base for AI agents. Mark anything — text, links, images — and MarkAI retrieves it automatically in every conversation, guessing your intent along the way.

---

## 🔒 Why Local-First Matters

| | MarkAI | Cloud-based memory |
|---|---|---|
| **Your data lives** | On your disk, in a single SQLite file | On someone else's server |
| **Who can read it** | Only you. No network, no API, no telemetry | The provider, their engineers, their vendors |
| **What you need** | Python 3 (built into macOS/Linux) | API keys, accounts, internet |
| **Offline?** | ✅ Fully functional | ❌ Dead |
| **Vendor lock-in?** | Zero. Your `.db` file goes wherever you go | Stuck with their export format |
| **Privacy for sensitive info** | Birthdays, contacts, passwords, ideas — stays on your machine | Hope you trust them |

> **MarkAI never phones home.** No embeddings API. No vector database cloud. Just Python stdlib + SQLite FTS5.

---

## ✨ Features

| # | Capability | Detail |
|---|-----------|--------|
| 🗄 | **Store** | Text, URLs, images — AI auto-generates title, tags, summary |
| 🔍 | **Gap Detection** | Spots ambiguous terms ("特币" → 比特币?) and asks before storing |
| 🌐 | **Web Enrichment** | Auto-fetches real-time data (prices, news) to fill in missing details |
| 🛡 | **Dedup** | Jaccard similarity check — warns if you're about to save a duplicate |
| 🔎 | **Search** | FTS5 full-text with CJK support, 3-tier fallback (phrase → OR → LIKE) |
| 📊 | **Ranking** | Tag boost + 7-day time decay — fresher, more relevant results first |
| 🧠 | **Augment** | Auto-injects matched knowledge into every conversation |
| 🎯 | **Intent Guessing** | "Birthday in 2 days? Need gift ideas?" — time-aware proactive suggestions |

---

## 📦 Install

```bash
npx skills add brickhu/markai
```

---

## 🌍 Multilingual Triggers

| 🇨🇳 | 🇬🇧 | 🇯🇵 | 🇰🇷 |
|-----|-----|-----|-----|
| 记住 · 存一下 · 备忘 | remember · save this · note to self | 覚えて · メモして | 기억해 · 저장해 |

Or just `/markai`.

---

## 🛠 CLI

```bash
markai save "content" --title "Title" --tags "tag1,tag2"
markai search "query" --ranked
markai stats
```

**Zero dependencies.** Python 3 stdlib + SQLite FTS5. Runs on macOS, Linux, and WSL.

---

## 📁 Data Layout

```
~/.agents/skills/markai/
├── data/
│   ├── brain.db          # All your knowledge in one file (SQLite + FTS5)
│   └── images/           # Image attachments
```

To back up: copy `brain.db`. To migrate: move `brain.db`. No export wizards needed.

---

---

# 📌 MarkAI — 捕捉 Agent 中的每一个火花。越来越懂你的 AI。

> 🇬🇧 [English version](#-markai--capture-every-spark-in-your-agent-ai-that-knows-you)

一个**完全本地化**的个人 AI 知识库 Skill。随手标记碎片知识——文本、链接、图片——MarkAI 会在每次对话中自动检索，并推测你的深层意图。

---

## 🔒 为什么本地优先至关重要

| | MarkAI | 云端记忆方案 |
|---|---|---|
| **数据存储** | 你的硬盘，一个 SQLite 文件 | 别人的服务器 |
| **谁能读取** | 只有你。无网络、无 API、无遥测 | 服务商、他们的工程师、他们的供应商 |
| **需要什么** | Python 3（macOS/Linux 自带） | API Key、账号、互联网 |
| **离线可用？** | ✅ 完全正常 | ❌ 无法使用 |
| **厂商锁定？** | 零。`.db` 文件随身带走 | 依赖他们的导出格式 |
| **敏感信息安全** | 生日、联系人、密码、灵感——全在本地 | 你只能选择信任他们 |

> **MarkAI 从不联网回传。** 不用 Embeddings API，不用云向量数据库。仅 Python 标准库 + SQLite FTS5。

---

## ✨ 功能一览

| # | 能力 | 说明 |
|---|------|------|
| 🗄 | **智能存储** | 文本、URL、图片——AI 自动生成标题、标签、摘要 |
| 🔍 | **缺口检测** | 识别模糊表述（"特币"→比特币？），存储前主动确认 |
| 🌐 | **联网补全** | 自动搜索实时数据（价格、新闻），补充缺失信息 |
| 🛡 | **重复检测** | Jaccard 字符相似度——即将重复存储时提醒你 |
| 🔎 | **全文搜索** | FTS5 中英文混搜，三层回退（短语→OR→LIKE） |
| 📊 | **智能排序** | 标签加权 + 7天时间衰减——越新越相关的排越前 |
| 🧠 | **对话增强** | 自动将匹配的知识注入上下文 |
| 🎯 | **意图猜解** | "生日还有2天？需要礼物建议吗？"——时间敏感主动提议 |

---

## 📦 安装

```bash
npx skills add brickhu/markai
```

---

## 🌍 多语言触发词

| 🇨🇳 | 🇬🇧 | 🇯🇵 | 🇰🇷 |
|-----|-----|-----|-----|
| 记住 · 存一下 · 备忘 | remember · save this · note to self | 覚えて · メモして | 기억해 · 저장해 |

或直接输入 `/markai`。

---

## 🛠 命令行

```bash
markai save "内容" --title "标题" --tags "标签1,标签2"
markai search "查询" --ranked
markai stats
```

**零依赖。** 仅需 Python 3 标准库 + SQLite FTS5。macOS、Linux、WSL 均可运行。

---

## 📁 数据目录

```
~/.agents/skills/markai/
├── data/
│   ├── brain.db          # 所有知识存在这一个文件里（SQLite + FTS5）
│   └── images/           # 图片附件
```

备份：复制 `brain.db`。迁移：移动 `brain.db`。不需要任何导出向导。

---

## 📄 License

MIT — do whatever you want. Your data is yours.
