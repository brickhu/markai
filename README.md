<p align="center">
  <img src="logo.svg" width="120" height="120" alt="MarkAI">
</p>

# MarkAI — Capture every spark in your agent. AI that knows you.

> 🇨🇳 [中文版本](README_CN.md)

[![skills.sh](https://skills.sh/b/brickhu/markai)](https://skills.sh/brickhu/markai)

MarkAI is a personal knowledge base that lives inside your AI agent. You tell it things in passing — a birthday, a link, an idea — and it brings them back exactly when you need them, automatically.

---

## 🤔 What problem does it solve?

You talk to your AI agent every day. But it forgets everything after each conversation. That person's birthday you asked about last week? Gone. That article you wanted to revisit? Forgotten. That insight you had at 2 AM? Lost.

**MarkAI gives your agent a memory that doesn't fade.**

---

## 💡 How it works — 30 seconds

```
You:    Remember: Lily's birthday is May 20, 2019.
MarkAI: ✅ Stored.

... 3 months later ...

You:    When is Lily's birthday?
MarkAI: May 20, 2019 — that's in 2 days! 🎂 Need gift ideas?
```

That's it. No commands to memorize. No folders to organize. Just talk.

---

## 🎯 When to use it

| You say | What happens |
|---------|-------------|
| "Remember: Bitcoin ETF approved Jan 2024" | Saves to knowledge base with auto-generated tags and summary |
| "Save this link: https://..." | Fetches the page, extracts key info, stores it |
| "Note to self: the API key is sk-xxx" | Stores securely on your machine (not the cloud) |
| "What was that React 19 release date?" | Searches your knowledge base, answers instantly |
| [A question about anything] | Automatically checks if you've saved something relevant |

---

## 🔒 100% Local. 100% Private.

| | MarkAI | Cloud alternatives |
|---|---|---|
| Where your data lives | Your hard drive | Someone else's computer |
| Who can read it | Only you | Their entire engineering team |
| Works offline | ✅ Yes | ❌ No |
| Vendor lock-in | None — it's a single `.db` file | Locked to their platform |
| Cost | Free forever | API fees, storage fees |

No sign-up. No API keys. No telemetry. Just Python and SQLite.

---

## 📦 Install

```bash
npx skills add brickhu/markai
```

Requires: Python 3 (pre-installed on macOS and Linux). Nothing else.

---

## 🗣️ Trigger words

Just say any of these naturally in conversation:

| 🇨🇳 | 🇬🇧 | 🇯🇵 | 🇰🇷 |
|-----|-----|-----|-----|
| 记住 · 存一下 · 备忘 | remember · save this · note to self | 覚えて · メモして | 기억해 · 저장해 |

Or type `/markai` for the dashboard.

---

## 🛠 Manage from terminal

```bash
markai stats                    # See what you've saved
markai search "keyword"         # Full-text search
markai list                     # Recent entries
markai export --format md       # Export everything as Markdown
```

---

## 📁 Your data, your control

```
~/.agents/skills/markai/data/
└── brain.db    ← Everything in one file
```

**Backup**: copy `brain.db`. **Migrate**: move `brain.db`. **Delete**: delete the folder. Simple.

---

## 📄 License

MIT.
