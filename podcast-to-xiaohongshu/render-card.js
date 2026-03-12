// 用 Puppeteer 渲染卡片并截图
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function renderCard(htmlPath, outputPath) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.setViewport({ width: 800, height: 800 });
  
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
  
  await page.screenshot({
    path: outputPath,
    type: 'png'
  });
  
  await browser.close();
  console.log(`Screenshot saved to ${outputPath}`);
}

const htmlPath = process.argv[2] || path.join(__dirname, 'output', 'card-temp.html');
const outputPath = process.argv[3] || path.join(__dirname, 'output', 'images', 'card.png');

renderCard(htmlPath, outputPath).catch(console.error);
