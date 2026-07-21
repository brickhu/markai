# 📌 MarkAI — Capture every spark in your agent. AI that knows you.

A local personal knowledge base skill for AI agents. Mark fragments of knowledge — text, images, links — and MarkAI retrieves them automatically to enrich every conversation.

## Install

```bash
npx skills add brickhu/markai
```

## What it does

- **Store**: Save text, URLs, and images with auto-generated metadata
- **Search**: FTS5 full-text search with CJK support + tag boost + time-decay ranking
- **Augment**: Automatically injects relevant knowledge into every conversation
- **Intent**: Guesses your deeper intent (e.g. birthday coming up → "Need gift ideas?")
- **Dedup**: Jaccard similarity check before every save

## Trigger (multilingual)

| 🇨🇳 | 🇬🇧 | 🇯🇵 | 🇰🇷 |
|-----|-----|-----|-----|
| 记住, 存一下, 备忘 | remember, save this, note to self | 覚えて, メモして | 기억해, 저장해 |

Or just `/markai`.

## CLI

```bash
markai save "content" --title "Title" --tags "tag1,tag2"
markai search "query" --ranked
markai stats
```

Zero dependencies — Python 3 stdlib + SQLite FTS5 only.

## Data

Everything stays local: `~/.agents/skills/markai/data/` — a single SQLite database + optional images directory.
