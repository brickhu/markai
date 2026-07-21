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

→ Step 1: Parse & spot gaps
  Detect: ambiguous terms, missing details, time-sensitive data

→ Step 2: Resolve gaps (if any)
  Ambiguity? → Ask user to confirm
  Real-time data? → web_fetch to enrich
  No gaps? → Skip to Step 3

→ Step 3: Duplicate check
  $ markai check "Bitcoin ETF approved in January 2024"
  → duplicates_found: 0 ✅

→ Step 4: Auto-extract metadata
  title: "Bitcoin ETF Approval"
  tags: "Bitcoin,ETF,crypto,regulation"
  summary: "SEC approved spot Bitcoin ETFs in January 2024"

→ Step 5: Store
  $ markai save "..." --title "Bitcoin ETF Approval" --tags "..." --summary "..."

→ Reply: ✅ Stored: Bitcoin ETF Approval (ID: abc123)
```

### ⚡ Information Gap Detection (MANDATORY before storing)

Before storing ANY entry, scan for these two gap types:

#### Gap Type 1: Ambiguity / Incomplete Info

If the user's input has unclear or incomplete terms, **ask to confirm** before storing.

| Signal | Example | Action |
|--------|---------|--------|
| Truncated term | "特币" → 比特币？ | Ask: *"你说的「特币」是指「比特币」吗？"* |
| Missing subject | "生日是5月20日" | Ask: *"这是谁的生日？"* |
| Vague pronoun | "他上周离职了" | Ask: *"「他」是指谁？"* |
| Partial number | "价格到了10万+" | Ask: *"是10万美金还是人民币？哪个币种？"* |

**Ask format:**

```
🤔 信息不太完整，确认一下：
- 「{term}」是指「{best guess}」吗？
```

#### Gap Type 2: Real-Time / Verifiable Data

If the content mentions data that can be verified or enriched via web search, **do it before storing**.

| Signal | Action |
|--------|--------|
| Price / market data ("价格10万", "涨了20%") | `web_fetch` current price, store both the user's observation + verified data |
| Event with known date ("上周获批") | Calculate exact date from today |
| News / announcement | Search to confirm and get exact details |
| Statistics ("市场份额第一") | Verify and add source |

**Enrich format:**

```
→ web_fetch to verify...
→ Enriched content:

原始: "记住：比特币价格已经到了10万+"
补充: "截至{date}，比特币价格为{verified_price}美金（用户观察到的是{original}）"

→ Store enriched version
→ Reply: ✅ 已存入并补充了最新数据：比特币当前 ${verified_price}（你观察到的 10万+ 是{timeframe}前的价格）
```

**Example — Combined gaps:**

```
User: 记住：特币当前价格已经到了10万+

→ Gap 1 (ambiguity): "特币" → 比特币？
  Reply: 🤔 你说的「特币」是指「比特币」吗？

  User: 是的

→ Gap 2 (real-time): "当前价格10万+"
  → web_fetch Bitcoin price
  → Current: $125,000 USD

→ Store enriched:
  title: "比特币价格观察"
  content: "比特币价格已达到10万+美金（2026年7月实际价格：$125,000 USD）"
  tags: "比特币,crypto,价格"

→ Reply:
  ✅ 已存入：比特币价格观察
  📊 联网补充：当前比特币 $125,000 USD（你观察到的 10万+ 是近期低点）

### Scenario 1b: Duplicate Detected

```
→ Step 3 (duplicate check) → found 1, similarity: 0.62
→ Reply: ⚠️ Similar entry exists: "Bitcoin ETF Approved" (62%). Store / Merge / Skip?
```

### Scenario 2: Image — Deep extraction, not just a caption 🖼️

**CRITICAL: Extract EVERY piece of information visible in the image. The description is the only thing that can be searched later.**

When the user sends an image with "remember" or "save this":

```
User: [sends a screenshot of a flight confirmation]
     Remember this.

→ Step 1: Deep visual analysis — extract ALL information
  You (the AI) must identify and record:
  - 📝 All visible text (OCR, labels, captions, numbers)
  - 📊 Structured data (tables, charts, prices, dates)
  - 👤 People, faces, names if visible
  - 🏷 Objects, brands, logos
  - 📍 Locations, addresses
  - 🎨 Colors, layout for context

→ Step 2: Generate a structured description
  Don't write "A screenshot of a flight ticket."
  Write:
  "Flight confirmation: CA1234, Beijing→Shanghai, 2026-08-15 08:30,
   Terminal 3, Seat 12A, Booking ref: ABC123, Gate B22"

→ Step 3: Copy image to data/images/
  $ cp /path/to/image.png ~/.agents/skills/markai/data/images/img_20260815.png

→ Step 4: Duplicate check on the description text

→ Step 5: Store
  title: "CA1234 北京→上海航班"
  tags: "旅行,航班,北京,上海"
  summary: "8月15日 CA1234 北京飞上海，T3，座位12A"

→ Reply:
  ✅ 已存入：CA1234 北京→上海航班
  🖼️ 已提取：航班号、日期、航站楼、座位号、订票编号
```

**Extraction checklist by image type:**

| Image type | Must extract |
|-----------|-------------|
| Screenshot / UI | All visible text, buttons, URLs, error messages, version numbers |
| Document / PDF scan | All text (OCR), dates, reference numbers, signatories |
| Chart / Graph | Data points, axes labels, trend direction, key numbers |
| Photo with people | Names, context, occasion, location, date if visible |
| Product / Object | Brand, model, price, specs, condition |
| Map / Floor plan | Address, landmarks, routes, distances |
| QR code / Barcode | Decoded content |
| Meme / Social post | Text, author, platform, context |
| Whiteboard / Handwritten | All text transcribed |

**If the image is unclear or contains unreadable text:**
- Note what IS visible
- Add tag `partial-read`
- Tell the user: *"⚠️ 图中{某部分}无法识别，已保存能提取的内容"*

**Fallback: If the current model/agent does NOT support vision:**

Some agents (or smaller models) cannot see images. In that case:

```
→ Detect: cannot process image
→ Save placeholder:
  $ markai save "Image stored: {filename}" \
      --title "📷 {filename}" \
      --tags "pending-vision,image" \
      --type image \
      --image "{filename}"
→ Reply:
  📷 图片已保存为 {filename}，但当前模型不支持视觉识别。
  下次用支持图片的 Agent 打开 markai 时，会自动补充内容描述。

  💡 提示：你也可以现在用文字告诉我图片里有什么，我来存。
```

When a vision-capable agent later encounters a `pending-vision` entry, it should:
1. Read the image file from `data/images/`
2. Run the full deep extraction workflow (Scenario 2)
3. Update the entry with the extracted content

```
→ Detected pending-vision entry: img_20260815.png
→ Reading image...
→ Extracted: "CA1234 flight, Beijing→Shanghai, Aug 15..."
→ $ markai update {id} --content "..." --title "..." --tags "旅行,航班" --summary "..."
→ Reply: 🖼️ 已补全：CA1234 北京→上海航班（之前存的图片）
```

### Scenario 3: URL — Fetch content, not the link 🔗

**CRITICAL: Never store a URL as the content. Always fetch and store the actual page content.**

When the user provides a URL (with or without "remember"):

```
User: Remember: https://openai.com/index/chatgpt-memory

→ Step 1: Fetch the actual content
  $ web_fetch https://openai.com/index/chatgpt-memory
  → Title: "Memory and new controls for ChatGPT"
  → Full text: "We're testing the ability for ChatGPT to remember things..."
  → Published: Feb 13, 2024

→ Step 2: Duplicate check on the fetched content
  $ markai check "OpenAI announced memory for ChatGPT..."
  → duplicates_found: 0 ✅

→ Step 3: Auto-extract metadata
  title: "ChatGPT Memory Feature"
  tags: "OpenAI,ChatGPT,memory,AI"
  summary: "OpenAI launched memory controls for ChatGPT, Feb 2024"

→ Step 4: Store the FULL fetched content + source URL
  $ markai save "Full article text here..." \
      --title "ChatGPT Memory Feature" \
      --tags "OpenAI,ChatGPT,memory,AI" \
      --summary "OpenAI launched memory controls for ChatGPT, Feb 2024" \
      --url "https://openai.com/index/chatgpt-memory"

→ Reply:
  ✅ 已存入：ChatGPT Memory Feature
  📄 已抓取全文内容（OpenAI, Feb 2024）
  🔗 来源: https://openai.com/index/chatgpt-memory
```

**What counts as "the content":**
- ✅ The article's full text (all paragraphs, key data, dates, quotes)
- ✅ Author, publish date, site name
- ❌ Just the URL
- ❌ Only the title
- ❌ A two-sentence summary without the body

**If `web_fetch` fails** (paywall, JS-only, blocked):
- Save what you can get + the URL
- Add tag `partial-fetch`
- Warn the user: *"⚠️ 只能抓取到部分内容，已保存链接供后续手动查看"*

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

Based on the above, {normal answer}...
```

### Step 4: Intent Guessing 🎯

After retrieving and answering, look at what the user asked + what you found, then **guess their deeper intent** and proactively offer the next step. Time-sensitive events are the strongest signal.

**Pattern matching rules:**

| Retrieved data | Context clue | Guess | Offer |
|---------------|-------------|-------|-------|
| Birthday / date | Today is near that date (≤3 days) | User wants to prepare a gift or greeting | "Only {N} days left! Need gift ideas or a birthday message?" |
| Birthday / date | Today IS that date | User might have forgotten | "It's today! 🎂 Want me to draft a quick greeting?" |
| Contact info (phone/email) | No obvious reason | User wants to reach out | "Want me to draft a message to them?" |
| Deadline / due date | Within this week | User is checking if they're on track | "That's {N} days away. Need help planning?" |
| How-to / technical note | User is asking a related question | User is solving a problem | "Want me to expand on this or walk through it step by step?" |
| URL / link saved | Recently stored | User wants to revisit or share | "Want me to open this or summarize it in detail?" |
| Past decision / preference | User is making a similar decision now | User wants consistency | "Based on your past preference, {suggestion}..." |

**Format:**

```
{Answer the question directly first}

💡 {Intent guess}: {Proactive offer}
```

**Example 1 — Birthday:**

```
User: When is Huxiwen's birthday?

→ Search: 胡昔文生日 is 2019-05-20
→ Today: 2026-05-19

Reply:
胡昔文的生日是2019年5月20日。

💡 明天就是她生日了，只有1天！需要我帮你准备生日祝福语或礼物建议吗？
```

**Example 2 — No time pressure:**

```
User: When is Huxiwen's birthday?

→ Search: 2019-05-20
→ Today: 2026-02-10

Reply:
胡昔文的生日是2019年5月20日（还有3个多月）。
```

When the date is far away, keep it simple — don't force an intent guess.

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
