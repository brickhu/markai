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

### Save a fact

```
You:    Remember: Bitcoin ETF approved in January 2024.
MarkAI: ✅ MarkAI stored: Bitcoin ETF Approval
        🏷 Bitcoin · ETF · crypto · regulation
```

### Save a link (full content fetched, not just URL)

```
You:    Save this: https://tech.meituan.com/2025/10/10/VSRM.html
MarkAI: ✅ MarkAI stored: VSRM — Verifiable Step-level Reward Model
        📄 Full article fetched (Meituan Tech, Oct 2025)
        🔗 https://tech.meituan.com/2025/10/10/VSRM.html
```

### Save a screenshot (AI extracts all visible info)

```
You:    [sends a flight confirmation screenshot]
        Remember this.
MarkAI: ✅ MarkAI stored: CA1234 Beijing→Shanghai
        🖼 Extracted: flight number, date, terminal, seat, booking ref
```

### Retrieve — automatic, no command needed

```
You:    When does the car insurance expire?
MarkAI: 📚 From your MarkAI:
        Tesla insurance renewal — due in August (about 10 days left)
        💡 Need me to compare plans?
```

### Proactive intent guessing

```
You:    When is Lily's birthday?
MarkAI: May 21, 2019 — that's in 2 days! 🎂
        💡 Want gift ideas or a birthday message?
```

### Update existing info — just say it again

```
You:    Remember: Lily's birthday is May 21 (not 20).
MarkAI: ✅ MarkAI updated: 胡昔文生日
        📝 Date corrected from May 20 to May 21
```

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
~/.markai/
└── brain.db    ← Everything in one file
```

**Backup**: copy `brain.db`. **Migrate**: move `brain.db`. **Delete**: delete the folder. Simple.

---

## 📄 License

MIT.
