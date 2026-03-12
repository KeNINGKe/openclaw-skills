---
name: ai-news-daily
description: >
  AI 新闻日报：每日精选 AI 行业重要新闻和深度内容。核心定位是「AI 行业发生了什么重要的事」，
  包括模型发布、公司动态、研究突破、行业观点、深度博客文章等。触发条件：(1) 定时任务触发 AI 日报，
  (2) 用户说「AI 日报」「AI 新闻」。注意：这个是新闻日报，不是玩法日报（玩法日报是另一个 skill）。
---

# AI 新闻日报

## 定位

**AI 行业每日重要新闻 + 深度内容精选。**

与「AI 玩法日报」的区别：
- 新闻日报 = 行业发生了什么（公司、产品、研究、政策）
- 玩法日报 = 人们用 AI 做了什么有趣的事（项目、应用、创意）

两者内容不要重叠。

## ⚠️ 信息时效性铁律

**必须优先检查一手信息源，避免信息滞后！**

教训案例：Anthropic 关于 AI 劳动力市场影响研究是 3月5日 发布的，但通过聚合媒体获取时已经滞后多日。

**强制规则：**
1. **搜索时强制 freshness: "day"** - 只要最近24小时的内容
2. **优先爬一手源** - 公司官网/博客 > 科技媒体 > 聚合站
3. **交叉验证时间** - 看到重要新闻时，去官网确认真实发布日期
4. **标注发布日期** - 每条内容必须注明原始发布时间

## 内容来源（按优先级）

### 一级源（必须检查，这是一手信息）

1. **AI 公司官方博客**（用 web_fetch 抓取）
   - https://openai.com/news/ — OpenAI 官方新闻
   - https://www.anthropic.com/news — Anthropic 官方新闻（注意不是 /research）
   - https://www.anthropic.com/research — Anthropic 研究论文
   - https://deepmind.google/discover/blog/ — Google DeepMind 博客
   - https://ai.meta.com/blog/ — Meta AI 博客

2. **技术博客精选**（参考 Karpathy 推荐的 HN 热门博客）
   - https://simonwillison.net/ — Simon Willison（AI 观察家）
   - https://lilianweng.github.io/ — Lilian Weng（OpenAI 研究）
   - https://karpathy.github.io/ — Andrej Karpathy

3. **Arxiv 最新论文**（用 web_fetch 抓取）
   - https://arxiv.org/list/cs.AI/recent — AI 方向最新论文
   - https://arxiv.org/list/cs.CL/recent — 计算语言学（NLP/LLM 相关）
   - https://arxiv.org/list/cs.LG/recent — 机器学习
   - 重点关注：被大量引用/讨论的论文、知名团队（OpenAI、DeepMind、Meta FAIR 等）的新论文
   - 筛选标准：重大突破或有实际应用价值的研究，跳过纯理论/小改进

4. **Hugging Face 趋势**（用 web_fetch 抓取）
   - https://huggingface.co/models?sort=trending — 热门模型趋势
   - https://huggingface.co/spaces?sort=trending — 热门 Spaces
   - https://huggingface.co/papers — Hugging Face Daily Papers（社区精选论文）
   - 重点关注：新上榜的热门模型、有趣的 demo、社区讨论度高的项目

### 二级源（补充，但要验证时效性）

5. **聚合站点**（仅作补充，必须回溯到原始来源验证时间）
   - https://hn.buzzing.cc/ — Hacker News 中文翻译
   - https://ai.hubtoday.app/ — AI Hub Today

6. **X/Twitter AI 圈**（用 bird CLI）
   ```bash
   bird search "AI announcement OR AI release OR AI paper min_faves:100" -n 10 --auth-token ... --ct0 ...
   bird search "from:OpenAI OR from:AnthropicAI OR from:GoogleDeepMind" -n 10 --auth-token ... --ct0 ...
   ```
   bird CLI 认证参数见 TOOLS.md。

7. **中文 AI 资讯**
   - https://hy.tencent.com/research — 腾讯混元研究

## 内容筛选标准

### ✅ 合格内容
- 重要模型/产品发布（GPT-5、Claude 4 等）
- AI 公司重大动态（融资、战略、合作）
- 突破性研究论文和成果
- 行业深度分析和观点文章
- AI 政策和监管动态
- 重要技术博客文章（不是教程，是有见解的分析）

### ❌ 不合格内容
- 水文、炒冷饭、标题党
- 纯教程类内容（"如何用 ChatGPT 写简历"）
- 个人 AI 项目展示（这属于玩法日报）
- 太细分的学术论文（除非是重大突破）

### 评分维度（参考 ai-daily-digest 项目）
每条候选内容从三个维度评估：
1. **重要性**（1-10）：对 AI 行业的影响程度
2. **时效性**（1-10）：是否是最近 24h 的新内容
3. **深度**（1-10）：是否有独特见解或深度分析

综合评分 = (重要性 × 0.4) + (时效性 × 0.3) + (深度 × 0.3)
取 Top 8-12 条。

## 每条内容的结构

1. **标题**：简洁有力的中文标题
2. **来源**：网站/作者名
3. **摘要**：2-3 句话的精华提炼
4. **原文链接**

## 输出格式

### 日报结构
```
标题：🤖 AI日报 - YYYY-MM-DD

📝 今日看点（3-5 句宏观趋势总结）

---

1-12 条正文内容（按重要性排序）

---

📊 扫描概况
- 扫描了 X 个源，共 Y 篇文章
- 精选 Z 篇
- 今日关键词：xxx, yyy, zzz
```

### 飞书文档创建
用 fix_doc4.js 模式手动构建 blocks（不要用 convert API）。

关键函数：
```javascript
const lark = require('C:/Users/event/AppData/Roaming/npm/node_modules/openclaw/node_modules/@larksuiteoapi/node-sdk');
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('C:/Users/event/.openclaw/openclaw.json','utf8'));
const client = new lark.Client({ appId: config.channels.feishu.appId, appSecret: config.channels.feishu.appSecret });

// Block 构建工具函数
function txt(content, bold) {
  return { text_run: { content, text_element_style: { bold: !!bold } } };
}
function link(content, url) {
  return { text_run: { content, text_element_style: { bold: false, link: { url } } } };
}
function heading1(text) { return { block_type: 3, heading1: { elements: [txt(text)], style: { align: 1 } }, parent_id: '' }; }
function heading2(text) { return { block_type: 4, heading2: { elements: [txt(text)], style: { align: 1 } }, parent_id: '' }; }
function para(...els) { return { block_type: 2, text: { elements: els, style: { align: 1 } }, parent_id: '' }; }
function bullet(...els) { return { block_type: 12, bullet: { elements: els, style: { align: 1 } }, parent_id: '' }; }
function divider() { return { block_type: 22, divider: {}, parent_id: '' }; }
```

## 发布

创建飞书文档后，将链接发送到日报群（chat_id: oc_d18f23a93a5dc7711ddee2e0618e0c32）。
