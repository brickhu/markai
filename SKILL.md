---
name: markai
description: Capture every spark in your agent. AI that knows you. A personal knowledge base / second brain. Triggers when the user says "remember", "save this", "note to self", "memorize", "记住", "存一下", "备忘", "기억해", "覚えて", "/markai", or sends content that looks like a knowledge fragment or inspiration worth keeping. Stores text, images, and URLs, then automatically retrieves relevant entries to augment every conversation.
---

# 📌 MarkAI · Personal AI Knowledge Base

> **Capture every spark in your agent. AI that knows you.**

A local second brain. Mark fragments of knowledge — text, images, links — and MarkAI retrieves them automatically to enrich every conversation.

---

## Trigger Keywords (Multilingual)

| Language | Keywords |
|----------|----------|
| 🇨🇳 Chinese | 记住, 存一下, 备忘, 记下来, 保存, 收录, 存档 |
| 🇬🇧 English | remember, save this, note to self, memorize, bookmark, store this, keep this |
| 🇯🇵 Japanese | 覚えて, 記憶して, メモして, 保存 |
| 🇰🇷 Korean | 기억해, 저장해, 메모해 |
| **Command** | `/markai`, `markai save`, `markai search` |

Also trigger automatically: when the user sends a standalone piece of knowledge or information (not a question or instruction).

---

## Core Loop

> **ingest → search → augment**

1. User marks something → **store** with auto-generated metadata
2. Every conversation turns → **search** for relevant entries
3. High-confidence matches → **augment** the response with context

---

## ⚠️ Pre-Storage: Duplicate Check (MANDATORY)

**Always run before storing:**

```bash
python3 ~/.agents/skills/markai/scripts/brain_cli.py check "<content to store>"
```

| Result | Action |
|--------|--------|
| `duplicates_found: 0` | Proceed to store |
| Similarity ≥ 0.5 | Warn user: *"Similar entry exists: **{title}** ({similarity}%). Store / Merge / Skip?"* |

---

## Auto-Generated Metadata (Your Job as AI)

When storing, you **must** generate these fields automatically — the user never types them:

| Field | Rule |
|-------|------|
| **title** | Concise title, ≤20 chars. Use the user's title if given. |
| **tags** | 2–5 tags. Mix languages (e.g. `React`, `前端`, `DeFi`). Prefer domain terminology. |
| **summary** | One sentence, ≤50 chars. Captures the essence — what makes this entry worth retrieving. |

---

## CLI Reference

### Ingest

```bash
# Text
markai save "content..." --title "Title" --tags "tag1,tag2" --summary "One-liner"

# URL (web_fetch first, then store)
markai save "fetched content..." --title "Page title" --url "https://..." --tags "tag1,tag2"

# Image (AI describes image first, then stores description + path)
markai save "AI-generated description..." --title "Image title" --tags "image,tag" --type image --image "file.png"
```

### Search & Retrieve

```bash
# Basic search (FTS5 → OR fallback → LIKE fallback, 3 layers)
markai search "query" --limit 10

# Ranked search (tag boost + time decay re-ranking)
markai search "query" --ranked --limit 5

# Duplicate check (run before every save)
markai check "content to check"
```

### Browse & Manage

```bash
markai list --limit 20          # Recent entries
markai get <id>                 # Full entry by ID
markai update <id> --tags "new" --summary "new summary"
markai delete <id>              # Delete by ID
markai stats                    # Dashboard: total, tag cloud, date range, weekly activity
markai export --format json     # or md
```

---

## Ingest Workflows

### Scenario 1: Text + "remember"

```
User: remember: Bitcoin ETF approved in January 2024

→ Step 1: Duplicate check
  $ markai check "Bitcoin ETF approved in January 2024"
  → duplicates_found: 0 ✅

→ Step 2: Auto-extract metadata
  title: "Bitcoin ETF Approval"
  tags: "Bitcoin,ETF,crypto,regulation"
  summary: "SEC approved spot Bitcoin ETFs in January 2024"

→ Step 3: Store
  $ markai save "..." --title "Bitcoin ETF Approval" --tags "..." --summary "..."

→ Reply: ✅ Stored: Bitcoin ETF Approval (ID: abc123)
```

### Scenario 1b: Duplicate Detected

```
→ Step 1: Duplicate check → found 1, similarity: 0.62
→ Reply: ⚠️ Similar entry exists: "Bitcoin ETF Approved" (62%). Store / Merge / Skip?
```

### Scenario 2: Image

1. You analyze the image and generate a text description
2. Copy image to `~/.agents/skills/markai/data/images/`
3. Store description + image path via `markai save`

### Scenario 3: URL

1. Use `web_fetch` to get page content
2. Duplicate check → extract title/tags/summary
3. Store with `--url` flag

### Scenario 4: Ambiguous — user didn't say "remember"

If the input looks like standalone knowledge (not a question), ask:
> 💡 This looks worth keeping. Save to MarkAI?

Do NOT auto-store without confirmation.

---

## Conversation Augmentation Workflow

### Step 1: Auto-Search

On every user question, extract core keywords and run:

```bash
markai search "<keywords>" --ranked --limit 5
```

### Step 2: Relevance Gate

| Signal | High ✅ | Medium 🤔 | Low ❌ |
|--------|--------|----------|--------|
| `_score` | > 3.0 | 1.0–3.0 | < 1.0 |
| Title/summary hit | Semantic match | Tag-only match | No match |
| **Action** | Inject into context | Mention: *"N related entries in your KB, want me to expand?"* | Say nothing |

### Step 3: Augment Format

```
📚 From your MarkAI:
- **{title}**: {summary} ({date})
- **{title}**: {summary} ({date})

Based on the above, {normal answer}...
```

---

## Management

| User says | Action |
|-----------|--------|
| `/markai` / 「查看知识库」 | `markai stats` → show dashboard |
| 「update xxx tags to yyy」 | `markai search` → find ID → `markai update --tags "yyy"` |
| 「delete xxx」 | `markai search` → show matches → confirm → `markai delete` |
| 「export」 | `markai export --format md` |
| 「search for xxx」 | `markai search "xxx" --limit 10` |

---

## Data Layout

```
~/.agents/skills/markai/
├── SKILL.md
├── scripts/
│   └── brain_cli.py       # Python 3 stdlib only
└── data/
    ├── brain.db           # SQLite + FTS5 full-text index
    └── images/            # Image attachments
```

---

## Best Practices

1. **Tag well**: Mix languages, use domain terms. `React`, `前端`, `blockchain`, `DeFi`.
2. **Title ≤20 chars**: Scannable at a glance.
3. **Summary = essence**: If someone reads nothing else, they should still get the point.
4. **Dedup is law**: Always `markai check` before saving. Warn at ≥50% similarity.
5. **Images need descriptions**: Images can't be text-searched. Your description is the only entry point.
6. **Augment precisely**: Only inject genuinely relevant entries. Don't spam.
7. **Update over pile-up**: Encourage users to refine existing entries rather than creating near-duplicates.
