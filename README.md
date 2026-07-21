# 📌 MarkAI — Capture every spark in your agent. AI that knows you.

> 🇨🇳 [中文版本](README_CN.md)

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

## 📄 License

MIT — do whatever you want. Your data is yours.
