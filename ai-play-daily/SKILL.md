---
name: ai-play-daily
description: >
  AI 玩法日报：搜集并编写每日 AI 玩法精选。核心定位是「普通人/开发者用 AI 做了什么有趣的事」，
  不是公司新闻、融资、发布会。触发条件：(1) 定时任务触发玩法日报，(2) 用户说「玩法日报」「AI 玩法」。
  绝对不要包含：公司融资、CEO 发言、模型发布、行业政策等新闻类内容——这些属于 AI 新闻日报的范畴。
---

# AI 玩法日报

## ⚠️ 核心原则（最重要，必须遵守）

**玩法 ≠ 新闻。** 每一条内容必须回答这个问题：「某个人/团队用 AI 做了什么具体的事？」

### ✅ 合格的内容（必须是这类）

- 有人用 Claude 写了一个完整的 SaaS 产品
- 开发者做了一个 AI Agent 自动打游戏的项目
- 设计师用 Midjourney 生成了一整套品牌视觉
- 有人用 GPT 分析自己 10 年的日记找到行为模式
- 独立开发者用 Cursor 3 天做出一个上线产品
- 有人让 AI Agent 自主管理一个 Twitter 账号涨粉到 10 万
- 开源项目：用 AI 自动生成单元测试并达到 90% 覆盖率
- Vibe coding 案例：非程序员用 AI 做出了可用的 App

### ❌ 不合格的内容（绝对不要出现）

- Anthropic 融资 300 亿美元（这是新闻）
- GPT-5.2 发布了新功能（这是产品发布）
- Google 发布 Gemini 3（这是公司新闻）
- Waymo 第六代上路（这是行业新闻）
- IBM 扩招（这是人事新闻）
- 某 CEO 说了什么（这是人物新闻）

### 🔑 判断标准

问自己：「这条内容的主角是一个具体的人/项目，还是一家公司？」
- 主角是人/项目 → ✅ 可以用
- 主角是公司/产品发布 → ❌ 不能用

## 内容来源（按优先级）

### 1. X/Twitter（最重要，必须搜索）

用 bird CLI 搜索。以下是有效的搜索策略：

```bash
# 核心搜索词（每次至少搜 3-5 个）
bird search "built with AI" -n 15 --auth-token ... --ct0 ...
bird search "vibe coding" -n 15 --auth-token ... --ct0 ...
bird search "I made this with Claude" -n 15 --auth-token ... --ct0 ...
bird search "AI agent project" -n 15 --auth-token ... --ct0 ...
bird search "built with cursor" -n 15 --auth-token ... --ct0 ...
bird search "shipped with AI" -n 10 --auth-token ... --ct0 ...
bird search "AI side project" -n 10 --auth-token ... --ct0 ...
bird search "made with chatgpt" -n 10 --auth-token ... --ct0 ...
bird search "AI workflow automation" -n 10 --auth-token ... --ct0 ...

# 高质量筛选（过滤噪音）
bird search "built with AI min_faves:50" -n 10 --auth-token ... --ct0 ...
bird search "AI project demo has:links" -n 10 --auth-token ... --ct0 ...
```

bird CLI 认证参数见 TOOLS.md 中的 X/Twitter 部分。

### 2. Hacker News Show HN

浏览器访问 https://news.ycombinator.com/show，重点看：
- 有 AI/LLM 相关的 Show HN 项目
- 点赞数 > 50 的优先
- 关注「个人做的项目」而非公司产品

### 3. Product Hunt 日榜

浏览器访问 https://www.producthunt.com/leaderboard/daily/，筛选：
- AI 相关的独立产品
- 个人/小团队做的工具
- 有创意的 AI 应用方式

### 4. GitHub Trending

浏览器访问 https://github.com/trending?since=daily，找：
- AI 相关的新开源项目
- 有趣的 AI 应用/工具
- 不要选纯基础设施类项目（除非玩法很有趣）

## 每条内容的结构

每条内容包含：
1. **标题**：一句话说清楚谁用 AI 做了什么
2. **描述**：2-3 句话展开，重点是「怎么做的」和「效果如何」
3. **玩法亮点**：产品经理视角的解读（用户体验、商业模式、增长策略、产品创新）
4. **来源链接**：原始链接

## 输出格式

用飞书云文档输出，使用 fix_doc4.js 模式手动构建 blocks。
每期 6-10 条内容，结尾加上「今日关键词」总结。

## 发布

创建飞书文档后，将链接发送到日报群（chat_id: oc_d18f23a93a5dc7711ddee2e0618e0c32）。
