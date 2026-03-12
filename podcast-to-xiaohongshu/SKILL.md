---
name: podcast-to-xiaohongshu
description: 从播客转录中提取热门选题，生成小红书文案+配图，并发布到小红书。适用于内容创作、知识分享、播客二次传播。
---

# Podcast to 小红书 Skill

从播客转录内容中提取适合小红书的选题，生成吸引人的标题、正文和配图，最终发布到小红书平台。

## 核心流程

```
播客转录 → 选题分析 → 文案生成 → 配图生成 → 小红书发布
```

## 前置条件

- 播客转录文件（来自 podcast-monitor skill）
- 浏览器自动化环境（用于小红书发布）
- 小红书账号已登录网页版

## 工作流程

### 1. 选题分析

从播客转录中提取 3-5 个潜在选题，每个选题评分：

**评分维度：**
- **话题热度**（⭐⭐⭐⭐⭐）：小红书用户关注度
- **争议性**（⭐⭐⭐⭐⭐）：容易引发讨论
- **实用性**（⭐⭐⭐⭐⭐）：对读者有价值
- **新鲜度**（⭐⭐⭐⭐⭐）：最近没发过类似内容

**选题原则：**
- 产品经理视角（用户体验、商业模式、增长策略）
- 避免纯技术/工程师视角
- 关注普通人关心的话题（职场、投资、生活方式）

**选题记录：**
- 保存到 `topics.json`，避免重复选题
- 格式：`{ "topics": [{ "title": "...", "score": 18, "date": "2026-03-09", "published": false }] }`

### 2. 文案生成

**小红书文案结构：**

```markdown
# [吸引人的标题] [emoji]

[开头段落：引发共鸣/制造悬念]

## 📊 [数据/事实]
- 具体数字
- 研究结论

## 🎯 [核心观点]
- 分点阐述
- 简洁清晰

## 💡 [实用建议]
1. 可操作的建议
2. 避免空话

---

[互动引导] 👇

#标签1 #标签2 #标签3
```

**文案风格：**
- 口语化、接地气
- 多用 emoji（但不过度）
- 分段清晰，每段 2-3 行
- 结尾引导互动（评论、点赞、收藏）

**字数控制：**
- 标题：15-25 字
- 正文：800-1200 字
- 标签：5-8 个

### 3. 配图生成

**使用 Canvas 工具生成文字卡片**

完全本地化方案，不依赖外部 API，稳定可控。

**设计原则：**
- 渐变背景（紫色/蓝色/橙色系）
- 白色卡片 + 圆角
- 突出核心数据/观点
- 字体层级清晰（标题 56px，数据 48px，说明 20px）
- 底部标注来源

**生成步骤：**

1. **准备数据**
   - 标题（拆成两行，第二行高亮）
   - Emoji（1个，代表主题）
   - 2组数据（数字 + 说明）
   - 标签（3-5个）
   - 来源（播客名称）

2. **生成 HTML**
   ```bash
   node generate-card.js \
     --title-line1 "AI 会抢走" \
     --title-line2 "你的工作吗？" \
     --emoji "🤖" \
     --stat1-number "85%" \
     --stat1-label "受影响的岗位" \
     --stat2-number "3年内" \
     --stat2-label "预计时间" \
     --tags "#AI #职场 #未来" \
     --source "来源：Hard Fork"
   ```

3. **Canvas 渲染截图**
   ```javascript
   // 1. 生成 HTML
   const result = await exec('node generate-card.js ...');
   const { htmlPath } = JSON.parse(result.stdout);
   
   // 2. Canvas 渲染
   await canvas({
     action: 'present',
     url: `file://${htmlPath}`,
     width: 800,
     height: 800
   });
   
   // 3. 截图
   const screenshot = await canvas({
     action: 'snapshot',
     outputFormat: 'png'
   });
   
   // 4. 保存
   fs.writeFileSync('output/images/card.png', screenshot);
   ```

**颜色方案：**
- 紫色系：`#667eea` → `#764ba2`
- 蓝色系：`#4facfe` → `#00f2fe`
- 橙色系：`#fa709a` → `#fee140`
- 绿色系：`#30cfd0` → `#330867`

### 4. 小红书发布

**发布方式：浏览器自动化**

使用 `browser` 工具自动化发布流程：

1. **打开小红书创作页面**
   ```javascript
   browser.open("https://creator.xiaohongshu.com/publish/publish")
   ```

2. **填写标题**
   ```javascript
   browser.act({ kind: "fill", ref: "标题输入框", text: "标题内容" })
   ```

3. **填写正文**
   ```javascript
   browser.act({ kind: "fill", ref: "正文输入框", text: "正文内容" })
   ```

4. **上传图片**
   ```javascript
   browser.upload({ paths: ["output/images/card.png"] })
   ```

5. **发布**
   ```javascript
   browser.act({ kind: "click", ref: "发布按钮" })
   ```

**注意事项：**
- 首次使用需要手动登录小红书网页版
- 发布前预览，确认格式正确
- 记录发布状态到 `published.json`

### 5. 发布记录

`published.json` 格式：

```json
{
  "published": [
    {
      "podcast": "Hard Fork",
      "episode": "Is A.I. Eating the Labor Market?",
      "topic": "AI 会抢走你的工作吗？",
      "publishDate": "2026-03-09",
      "url": "https://www.xiaohongshu.com/...",
      "stats": {
        "views": 0,
        "likes": 0,
        "comments": 0
      }
    }
  ]
}
```

## 文件结构

```
skills/podcast-to-xiaohongshu/
├── SKILL.md                    # 本文件
├── topics.json                 # 选题库
├── published.json              # 发布记录
├── templates/
│   ├── card-template.html      # 文字卡片模板
│   └── dalle-prompts.txt       # DALL-E 提示词模板
└── output/
    ├── drafts/                 # 文案草稿
    └── images/                 # 生成的配图
```

## 使用示例

**手动触发：**
```
用户：从最新的播客转录生成一篇小红书内容
```

**定时任务：**
- 每周 2-3 次，从未发布的播客中选择 1 期
- 生成文案+配图
- 发送预览给用户确认
- 确认后发布

## 优化方向

1. **选题优化**
   - 分析小红书热搜榜，结合播客内容
   - 追踪已发布内容的数据，优化选题策略

2. **配图优化**
   - 多种卡片模板（数据型、观点型、故事型）
   - 支持多图发布（1-9 张）

3. **发布优化**
   - 最佳发布时间分析（早 8 点、晚 9 点）
   - 自动回复评论（常见问题）

4. **数据追踪**
   - 定期抓取发布内容的数据（浏览、点赞、评论）
   - 分析哪类选题表现最好

## 错误处理

**选题失败：**
- 播客内容不适合小红书（太技术、太小众）
- 跳过该期，处理下一期

**配图生成失败：**
- HTTP 服务器启动失败 → 重试或使用备用端口
- 浏览器截图失败 → 检查页面是否加载完成

**发布失败：**
- 小红书登录过期 → 提示用户重新登录
- 内容违规 → 记录原因，调整文案重试
- 网络问题 → 保存草稿，稍后重试

## 配置

在 `TOOLS.md` 中记录：
- 小红书账号信息（用户名，不记录密码）
- 发布偏好（最佳时间、标签偏好）
- 配图风格偏好（颜色、字体）
