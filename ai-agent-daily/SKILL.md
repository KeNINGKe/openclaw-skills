---
name: ai-agent-daily
description: >
  AI Agent 项目日报：每日精选 AI Agent 在垂直领域的落地应用。核心定位是「Agent + 行业」的具体案例，
  重点关注 Agent 在金融、医疗、法律、教育、电商、招聘、安全、DevOps 等垂直场景的实际应用。
  触发条件：(1) 定时任务触发 Agent 日报，(2) 用户说「Agent 日报」「AI Agent 项目」。
  与玩法日报的区别：玩法日报关注「人用 AI 做了什么有趣的事」，Agent 日报关注「Agent 在哪些垂直领域落地了」。
---

# AI Agent 项目日报

## ⚠️ 核心原则

**聚焦垂直落地。** 每一条内容必须是 Agent 在某个具体行业/场景的应用案例。

### ✅ 合格的内容（优先级从高到低）

- **Agent + 金融**：交易 Agent、风控 Agent、投研 Agent、财务自动化
- **Agent + 医疗**：诊断辅助、病历分析、药物研发、患者管理
- **Agent + 法律**：合同审查、案例检索、合规检查
- **Agent + 电商/营销**：客服 Agent、广告投放、用户增长、内容生成
- **Agent + 招聘/HR**：简历筛选、面试安排、人才匹配
- **Agent + 安全**：渗透测试、漏洞扫描、威胁检测
- **Agent + DevOps**：运维自动化、故障排查、监控告警
- **Agent + 教育**：个性化辅导、作业批改、课程生成
- **Agent + 研究**：论文检索、数据分析、实验设计
- **Agent + 创意**：设计、音乐、视频、游戏制作
- 其他垂直领域的 Agent 应用

### ❌ 不合格的内容

- 通用 Agent 框架（LangGraph、CrewAI 等，除非有明确的垂直场景）
- 纯编码 Agent（这属于玩法日报的范畴）
- 公司融资新闻
- 纯理论论文（除非有开源实现）
- 纯基础设施（记忆、MCP 工具链等，除非服务于特定垂直场景）

### 🔑 判断标准

问自己：「这个 Agent 解决了哪个行业的什么具体问题？」
- 能说清行业 + 问题 → ✅ 收录
- 只是通用工具 → ❌ 不收

## 内容来源（按优先级）

### 1. GitHub Trending

- 每日 trending 中的 AI Agent 相关项目
- 关注 star 增长速度和 fork 数
- 重点看 description 中包含 agent、MCP、tool、autonomous 等关键词的项目

### 2. Hacker News

用 Algolia API 搜索：
- `agent LLM autonomous` (Show HN)
- `coding agent Claude Cursor`
- `MCP tool framework`
- `AI agent` (points > 10)

### 3. X/Twitter

用 bird CLI 搜索（认证参数见 TOOLS.md）：
- `AI agent open source`
- `MCP server tool`
- `coding agent framework`
- `autonomous agent project`

### 4. Reddit

- r/LocalLLaMA
- r/MachineLearning
- r/artificial

## 每条内容的结构

1. **项目名 + 垂直领域 + 一句话定位**
2. **解决什么问题**：这个行业原来的痛点是什么
3. **Agent 怎么做**：2-3 句话说清楚 Agent 的工作方式
4. **商业洞察**：产品经理视角——市场规模、商业模式、竞争格局、增长潜力
5. **数据**：GitHub stars、用户量、融资情况等
6. **链接**

## 输出格式

用飞书云文档输出，使用 write action。
每期 6-10 个项目，按垂直领域分类组织，如：
- 💰 金融/交易
- 🏥 医疗/健康
- ⚖️ 法律/合规
- 🛒 电商/营销
- 🔒 安全/运维
- 🎓 教育/研究
- 🎨 创意/内容

结尾加「本期行业洞察」总结。

## 发布

创建飞书文档后，将链接发送到日报群（chat_id: oc_d18f23a93a5dc7711ddee2e0618e0c32）。
定时：每天中午 12:30。
