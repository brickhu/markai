<p align="center">
  <img src="logo.svg" width="120" height="120" alt="MarkAI">
</p>

# MarkAI — 每个 Agent 都共享一个大脑

> *Capture sparks in every agent. AI that knows you.*

> 🇬🇧 [English version](README.md)

MarkAI 是一个住在你 AI Agent 里的个人知识库。你随口告诉它的事——一个生日、一条链接、一个灵感——它会在你最需要的时刻自动想起来。

---

## 🤔 解决什么问题？

你会在不同场景用不同的 Agent——Kun 日常聊天、Claude Code 写代码、Cursor 做前端。但**每个 Agent 都有自己的记忆**。在一个 Agent 里存的 Lily 生日，其他的都不知道。收藏的那篇文章，困在了一个工具里。

**MarkAI 是所有 Agent 共享的一个大脑。一个学会的，全知道。**

---

## 💡 30 秒看懂怎么用

```
你（在 Kun 里）：   记住：莉莉的生日是 2019 年 5 月 20 日。
MarkAI:             ✅ 已存入。

... 切换到 Claude Code 写代码 ...

你（在 Claude 里）：莉莉生日哪天？
MarkAI:             5 月 20 日——就剩 2 天了！🎂 需要礼物建议吗？
```

就这样。一个 Agent 里存一次，所有 Agent 都知道。不需要导出导入。

---

## 🎯 什么时候用？

### 一个完整的记忆旅程 —— 从学到用

```
你（在 Kun 里）：   记住：莉莉喜欢的花是牡丹。
MarkAI:             ✅ MarkAI 已存入：莉莉喜欢牡丹
                    🏷 Lily · 花 · 偏好

你（在 Kun 里）：   记住：莉莉说她想要一个惊喜派对。
MarkAI:             ✅ MarkAI 已存入：莉莉想要惊喜派对
                    🏷 Lily · 派对 · 惊喜 · 心愿单

... 两个月后，你在 Cursor 里做待办事项 App ...

你（在 Cursor 里）：关于莉莉我知道些什么？
MarkAI:             📚 从你的知识库找到：
                    1. 莉莉生日：5 月 21 日
                    2. 莉莉喜欢牡丹 🌸
                    3. 莉莉想要惊喜派对 🎉

                    💡 她生日就剩 2 天了！方案：
                    - 买牡丹 ✓
                    - 惊喜派对——她说过想要的！
                    - 礼物建议？我可以帮忙。
```

### 记一条事实

```
你:     记住：比特币 ETF 2024 年 1 月获批。
MarkAI: ✅ MarkAI 已存入：比特币 ETF 获批
        🏷 比特币 · ETF · 加密货币 · 监管
```

### 存一个链接（自动抓取全文，不只是存 URL）

```
你:     收藏这个：https://tech.meituan.com/2025/10/10/VSRM.html
MarkAI: ✅ MarkAI 已存入：VSRM—可验证过程奖励提升大模型推理效率
        📄 已抓取全文（美团技术，2025年10月）
        🔗 https://tech.meituan.com/2025/10/10/VSRM.html
```

### 存一张截图（AI 提取所有可见信息）

```
你:     [发了一张航班确认截图]
        记住这个。
MarkAI: ✅ MarkAI 已存入：CA1234 北京→上海
        🖼 已提取：航班号、日期、航站楼、座位号、订票编号
```

### 自动检索 —— 什么都不用说

```
你:     车险什么时候到期？
MarkAI: 📚 从你的知识库找到：
        特斯拉车险8月续保——还有约10天
        💡 需要对比保险方案吗？
```

### 主动意图猜解

```
你:     莉莉生日哪天？
MarkAI: 5月21日——就剩2天了！🎂
        💡 需要礼物建议或生日祝福语吗？
```

### 更新已有信息 —— 再说一遍就行

```
你:     记住：莉莉生日是5月21号，不是20号。
MarkAI: ✅ MarkAI 已更新：莉莉生日
        📝 日期已修正
```

---

## 🔒 100% 本地。100% 隐私。

| | MarkAI | 云端方案 |
|---|---|---|
| 数据存在哪 | 你的硬盘 | 别人的服务器 |
| 谁能看到 | 只有你 | 他们的整个工程团队 |
| 离线能用吗 | ✅ 能 | ❌ 不能 |
| 厂商锁定 | 没有——就一个 `.db` 文件 | 绑死在他们平台 |
| 费用 | 永久免费 | API 费、存储费 |

不用注册。不用 API Key。不传遥测。就 Python + SQLite。

---

## 🧩 一个知识库，任何 Agent 都能用

MarkAI 是一个 SKILL.md——AI Agent 能力的通用格式。支持 **Kun**、**Claude Code**、**Cursor**、**Windsurf**、**Gemini**、**Copilot** 等任何支持 SKILL.md 的 Agent。

**你的知识是统一的。换 Agent，知识不变。**

数据不绑定任何一个工具。它统一存在 `~/.markai/brain.db` 里——一个文件，所有 Agent 共享。换 Agent 时安装一下 MarkAI，记忆立刻就有。不需要导出、导入、迁移。

---

## 📦 安装

```bash
npx skills add brickhu/markai
```

只需 Python 3（macOS 和 Linux 自带）。零额外依赖。

---

## 🗣️ 直接说就行

不用记命令。MarkAI 会自动识别你的意图：

| 语言 | 触发词 |
|------|--------|
| 🇨🇳 中文 | 记住，保存，收藏，备忘，存一下，存档，记下来，收录，保存起来 |
| 🇬🇧 English | remember, save this, note to self, memorize, bookmark, keep this |
| 🇯🇵 日本語 | 覚えて，記憶して，メモして，保存 |
| 🇰🇷 한국어 | 기억해，저장해，메모해 |
| 🌍 Any | 直接说就行，MarkAI 会识别你要存储的意图 |

或输入 `/markai` 查看知识库。<｜end▁of▁thinking｜>

---

## 🛠 终端管理

```bash
markai stats                    # 看看存了多少
markai search "关键词"           # 全文搜索
markai list                     # 最近条目
markai export --format md       # 导出为 Markdown
```

---

## 📁 你的数据，你说了算

```
~/.markai/
└── brain.db    ← 所有知识在这一个文件里
```

**备份**：复制 `brain.db`。**迁移**：移动 `brain.db`。**删除**：删掉文件夹。就这么简单。

---

## 📄 License

MIT.
