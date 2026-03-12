---
name: podcast-monitor
description: Podcast RSS monitoring, transcription (Groq Whisper), and summarization system. Activate when user mentions podcasts, RSS feeds, transcription, podcast summaries, or wants to set up podcast monitoring.
---

# Podcast Monitor Skill

Monitor podcast RSS feeds, auto-download + transcribe new episodes via Groq Whisper API, generate summaries, and push to messaging channels.

## Prerequisites

- Node.js (v18+)
- ffmpeg (for compressing large audio files)
- Groq API key (for Whisper transcription)
- Proxy if needed for external API access

## Setup

### 1. Initialize workspace

Create a `podcast/` directory in the workspace with the required structure:

```
podcast/
├── config.json      — podcast feeds + API key
├── state.json       — processing state (auto-generated)
├── pushed.json      — push tracking (auto-generated)
├── podcast.js       — main script (bundled)
├── audio/           — downloaded audio files
└── transcripts/     — transcription output
```

### 2. Configure feeds

Create `config.json`:

```json
{
  "groq_api_key": "<GROQ_API_KEY>",
  "podcasts": [
    { "name": "Planet Money", "feed": "https://feeds.npr.org/510289/podcast.xml", "lang": "en" },
    { "name": "商业就是这样", "feed": "http://www.ximalaya.com/album/46587439.xml", "lang": "zh" }
  ]
}
```

Fields:
- `groq_api_key`: Groq API key for Whisper transcription
- `podcasts[].name`: Display name
- `podcasts[].feed`: RSS feed URL
- `podcasts[].lang`: Language code (`en`, `zh`, etc.) for transcription accuracy

### 3. Copy the script

Copy `scripts/podcast.js` to `podcast/podcast.js`.

### 4. Initialize tracking

Create `podcast/pushed.json`:

```json
{ "pushed": [] }
```

## Usage

### CLI Commands

Run from the `podcast/` directory:

```bash
node podcast.js check     # Check RSS feeds for new episodes
node podcast.js process   # Download + transcribe one pending episode
node podcast.js list      # List processed and pending episodes
```

- `check` fetches the latest 3 episodes from each feed, adds new ones to pending
- `process` handles one pending episode at a time (download → compress if needed → transcribe)
- Each run processes only ONE episode to avoid timeouts (Lex Fridman episodes can be 3-4 hours)

### Cron Setup

Set up a cron job (e.g., twice daily) with this workflow:

1. Run `node podcast.js check` to detect new episodes
2. Run `node podcast.js process` to transcribe one pending episode
3. Read `pushed.json` and `state.json` to find untranscribed episodes
4. Read the transcript file, generate a Chinese summary (500-800 chars)
5. **必须包含「💰 投资机会」部分**（见 Summary Format），分析播客内容中潜在受益的行业或标的
6. **双存储写入**：
   - **飞书云文档**：使用 `feishu_doc` 创建摘要文档 + 完整转录文档
   - **Obsidian**：使用 `write` 工具创建 Markdown 文件到 `D:\Obsidian\播客\摘要\` 和 `D:\Obsidian\播客\转录\`
   - 记录文档 URL/路径到 `pushed.json`
7. Update `pushed.json` with the pushed episode key and doc URLs

### Summary Delivery — 双存储模式（飞书 + Obsidian）

**飞书云文档结构：**
```
播客转录/
├── 摘要文档/
│   └── YYYY-MM-DD_节目名_摘要.docx
└── 完整转录/
    └── YYYY-MM-DD_节目名_全文.docx
```

**Obsidian 结构：**
```
D:\Obsidian\播客\
├── 摘要/
│   └── YYYY-MM-DD_节目名_摘要.md
└── 转录/
    └── YYYY-MM-DD_节目名_全文.md
```

**每期播客创建两个文档：**

**1. 摘要文档**（`播客转录/摘要文档/YYYY-MM-DD_节目名_摘要.docx`）：
```markdown
# 🎙️ <Podcast Name> — <Episode Title>

<Brief intro paragraph>

## 📌 核心观点

1. <Point 1>
2. <Point 2>
3. <Point 3>

## 💬 金句

> "<Notable quote from the episode>"

## ⭐ 一句话评价

<One-line review>

---

## 💰 投资机会

| 标的 | 利好逻辑 | 时间维度 | 确定性 |
|------|---------|---------|--------|
| <行业/公司/股票代码/加密货币> | <为什么利好，逻辑链条> | 短期/中期/长期 | 高/中/低 |
| <行业/公司/股票代码/加密货币> | <为什么利好，逻辑链条> | 短期/中期/长期 | 高/中/低 |

**⚠️ 风险提示：** <需要警惕的标的或趋势>
```

**2. 完整转录文档**（`播客转录/完整转录/YYYY-MM-DD_节目名_全文.docx`）：
```markdown
# <Podcast Name> — <Episode Title> — 完整转录

**发布日期：** <episode publish date>
**转录时间：** <transcription timestamp>
**时长：** <duration>

---

<Full transcript text here>
```

**⚠️ 【铁律 - 已因遗漏被批评 7 次】投资机会部分必须包含在摘要文档中，不能省略。**

Content preference: product manager perspective (user experience, business models, growth strategies, product innovation). Avoid pure engineering/technical focus.

### Feishu Integration

使用 `feishu_doc` 工具创建文档：

1. **文件夹 token 配置**：
   - 摘要文档文件夹和完整转录文件夹的 token 记录在 `TOOLS.md`（不是 config.json）
   - 查看 TOOLS.md 中的 "播客转录文件夹" 部分获取 token

2. **创建摘要文档**：
   ```javascript
   // 使用 feishu_doc write（推荐）或 create
   // folder_token: 从 TOOLS.md 获取摘要文档文件夹 token
   // title: YYYY-MM-DD_节目名_标题关键词
   // content: markdown 格式的摘要内容
   ```

3. **创建转录文档**：
   ```javascript
   // 使用 feishu_doc write
   // folder_token: 从 TOOLS.md 获取完整转录文件夹 token
   // title: YYYY-MM-DD_节目名_全文
   // content: 完整转录文本
   ```

4. **重复推送检查**：
   - 在生成摘要前，先检查 `pushed.json` 中是否已存在该集的 key
   - 避免重复推送同一期播客

### Obsidian Integration

使用 `write` 工具直接写入 Markdown 文件：

1. **确保目录存在**：
   ```bash
   mkdir -p "D:\Obsidian\播客\摘要"
   mkdir -p "D:\Obsidian\播客\转录"
   ```

2. **摘要文档格式**（`摘要/YYYY-MM-DD_节目名_标题关键词.md`）：
   ```markdown
   ---
   date: 2026-03-06
   podcast: Planet Money
   episode: Episode Title
   tags: [podcast, 摘要, 投资机会]
   ---
   
   # 🎙️ Planet Money — Episode Title
   
   <简介段落>
   
   ## 📌 核心观点
   1. ...
   
   ## 💬 金句
   > "..."
   
   ## ⭐ 一句话评价
   ...
   
   ## 💰 投资机会
   
   | 标的 | 利好逻辑 | 时间维度 | 确定性 |
   |------|---------|---------|--------|
   | 英伟达(NVDA) | AI 算力需求持续增长 | 中长期 | 高 |
   | 比特币 | 机构采用加速 | 短期 | 中 |
   
   **⚠️ 风险提示：** ...
   ```

3. **完整转录格式**（`转录/YYYY-MM-DD_节目名_全文.md`）：
   ```markdown
   ---
   date: 2026-03-06
   podcast: Planet Money
   episode: Episode Title
   duration: 45:00
   tags: [podcast, 转录]
   ---
   
   # 完整转录
   
   <full transcript>
   ```

### Push Tracking

`pushed.json` tracks which episodes have been summarized and pushed:

```json
{
  "pushed": [
    "Planet Money::Episode Title Episode Title",
    "商业就是这样::Vol.244 ..."
  ]
}
```

The key format matches `state.json`'s `processed` keys. After pushing a summary, append the key to the `pushed` array.

## Troubleshooting

- Large files (>24MB): Script auto-compresses with ffmpeg. If ffmpeg is missing, install it.
- Proxy issues: Script defaults to `http://127.0.0.1:7890`. Set `HTTPS_PROXY` env var to override.
- Ximalaya encoding: Chinese podcast titles may show garbled in state.json due to PowerShell encoding. This is cosmetic; transcription still works.
- Groq rate limits: If transcription fails, retry on next cron run.

## Error Recovery

**飞书 API 失败：**
- 检查 folder_token 是否正确（从 TOOLS.md 获取）
- 确认 Bot 有文件夹写入权限
- 如果创建失败，记录错误到日志，下次 cron 重试

**Obsidian 目录不存在：**
- 使用 `exec` 运行 `mkdir` 创建目录（Windows: `mkdir "D:\Obsidian\播客\摘要"`）
- 如果创建失败，跳过 Obsidian 写入，只推送飞书文档

**重复推送检查：**
- 每次生成摘要前，先读取 `pushed.json`
- 检查当前 episode key 是否已在 `pushed` 数组中
- 如果已存在，跳过该集，处理下一集

## 投资机会分析提示词

生成摘要时，使用以下提示词模板分析投资机会：

```
分析这期播客中的投资机会：

1. 哪些行业/公司被正面提及或受益？
2. 哪些趋势可能带来投资机会？（技术、政策、市场变化）
3. 有哪些风险信号需要警惕？
4. 时间维度：短期（<6个月）、中期（6-18个月）、长期（>18个月）
5. 确定性评级：高（播客明确看好）、中（逻辑合理但有变数）、低（推测性）

输出格式：
| 标的 | 利好逻辑 | 时间维度 | 确定性 |
|------|---------|---------|--------|
| ... | ... | ... | ... |

风险提示：列出需要警惕的标的或趋势
```
