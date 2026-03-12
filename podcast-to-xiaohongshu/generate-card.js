// 生成小红书配图卡片
// 用法: node generate-card.js --title "标题" --emoji "🎯" --stat1-number "85%" --stat1-label "用户留存率" ...

const fs = require('fs');
const path = require('path');

// 解析命令行参数
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '').replace(/-/g, '_').toUpperCase();
  params[key] = args[i + 1];
}

// 默认值
const defaults = {
  GRADIENT_START: '#667eea',
  GRADIENT_END: '#764ba2',
  EMOJI: '💡',
  TITLE_LINE1: '这是标题第一行',
  TITLE_LINE2: '这是标题第二行',
  STAT1_NUMBER: '100%',
  STAT1_LABEL: '数据指标1',
  STAT2_NUMBER: '200+',
  STAT2_LABEL: '数据指标2',
  TAGS: '#AI #产品 #增长',
  SOURCE: '来源：播客名称'
};

// 合并参数
const data = { ...defaults, ...params };

// 读取模板
const templatePath = path.join(__dirname, 'templates', 'card-template.html');
let html = fs.readFileSync(templatePath, 'utf-8');

// 替换变量
Object.keys(data).forEach(key => {
  const regex = new RegExp(`{{${key}}}`, 'g');
  html = html.replace(regex, data[key]);
});

// 输出到临时文件
const outputPath = path.join(__dirname, 'output', 'card-temp.html');
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html, 'utf-8');

console.log(JSON.stringify({
  success: true,
  htmlPath: outputPath,
  data: data
}));
