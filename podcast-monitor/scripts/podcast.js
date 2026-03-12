/**
 * 播客监控 + 转录 + 总结系统
 * 
 * 用法:
 *   node podcast.js check    — 检查所有播客是否有新一期
 *   node podcast.js process  — 处理（下载+转录+总结）所有待处理的新一期
 *   node podcast.js list     — 列出已处理的所有期
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const https = require('https');
const http = require('http');

const CONFIG_FILE = path.join(__dirname, 'config.json');
const STATE_FILE = path.join(__dirname, 'state.json');
const AUDIO_DIR = path.join(__dirname, 'audio');
const TRANSCRIPT_DIR = path.join(__dirname, 'transcripts');

// 确保目录存在
[AUDIO_DIR, TRANSCRIPT_DIR].forEach(d => { if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true }); });

// 刷新 PATH（winget 安装的工具可能不在当前 PATH 中）
try {
  const newPath = execSync('powershell -Command "[System.Environment]::GetEnvironmentVariable(\'Path\',\'Machine\') + \';\' + [System.Environment]::GetEnvironmentVariable(\'Path\',\'User\')"', { encoding: 'utf8' }).trim();
  process.env.PATH = newPath;
} catch (e) { /* ignore */ }

// 默认代理（如果环境变量没设置）
if (!process.env.HTTPS_PROXY && !process.env.HTTP_PROXY && !process.env.ALL_PROXY) {
  process.env.HTTPS_PROXY = 'http://127.0.0.1:7890';
}

function loadConfig() { return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')); }
function loadState() {
  if (fs.existsSync(STATE_FILE)) return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  return { processed: {}, pending: [] };
}
function saveState(s) { fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2)); }

// 用 PowerShell 下载文件（绕过 Node.js 代理问题）
function downloadFile(url, dest) {
  console.log(`  下载中: ${url.slice(0, 80)}...`);
  const cmd = `powershell -Command "Invoke-WebRequest -Uri '${url}' -OutFile '${dest}' -UseBasicParsing"`;
  execSync(cmd, { timeout: 600000 }); // 10分钟超时
  const stat = fs.statSync(dest);
  console.log(`  下载完成: ${(stat.size / 1024 / 1024).toFixed(1)} MB`);
  return stat.size;
}

// 用 PowerShell 获取 RSS，输出 JSON 格式避免解析问题
function fetchRSS(url) {
  const cmd = `powershell -Command "$r = [xml](Invoke-WebRequest -Uri '${url}' -UseBasicParsing).Content; $items = $r.rss.channel.item | Select-Object -First 3; $out = @(); foreach($i in $items) { $enc = if($i.enclosure.url){$i.enclosure.url}else{''}; $t = if($i.title.'#cdata-section'){$i.title.'#cdata-section'}elseif($i.title -is [string]){$i.title}else{[string]$i.title}; $out += @{title=$t; pubDate=[string]$i.pubDate; audioUrl=$enc} }; $out | ConvertTo-Json -Compress"`;
  const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
  const parsed = JSON.parse(result);
  // PowerShell 单个对象不是数组
  return Array.isArray(parsed) ? parsed : [parsed];
}

// Groq Whisper 转录（分片上传，每片 < 25MB）
function transcribeWithGroq(audioPath, lang, apiKey) {
  const stat = fs.statSync(audioPath);
  const sizeMB = stat.size / 1024 / 1024;
  console.log(`  转录中 (${sizeMB.toFixed(1)} MB, lang=${lang})...`);

  // Groq Whisper 限制 25MB，大文件需要先转换/分片
  if (sizeMB > 24) {
    console.log(`  文件过大，尝试压缩...`);
    const compressedPath = audioPath + '.compressed.mp3';
    try {
      // 尝试用 ffmpeg 压缩（如果有的话）
      execSync(`ffmpeg -i "${audioPath}" -b:a 32k -ac 1 -ar 16000 "${compressedPath}" -y`, { timeout: 300000 });
      audioPath = compressedPath;
      console.log(`  压缩后: ${(fs.statSync(compressedPath).size / 1024 / 1024).toFixed(1)} MB`);
    } catch (e) {
      // 没有 ffmpeg，用 PowerShell 分片
      console.log(`  无 ffmpeg，将分段转录...`);
      return transcribeChunked(audioPath, lang, apiKey);
    }
  }

  return callGroqWhisper(audioPath, lang, apiKey);
}

function callGroqWhisper(audioPath, lang, apiKey) {
  // 用 curl.exe 调 Groq API，加 --proxy 支持
  const proxy = process.env.HTTPS_PROXY || process.env.HTTP_PROXY || process.env.ALL_PROXY || '';
  const proxyArg = proxy ? `--proxy "${proxy}"` : '';
  const cmd = `curl.exe -s --max-time 300 ${proxyArg} -X POST "https://api.groq.com/openai/v1/audio/transcriptions" -H "Authorization: Bearer ${apiKey}" -F "file=@${audioPath}" -F "model=whisper-large-v3" -F "language=${lang}" -F "response_format=text"`;
  const result = execSync(cmd, { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024, timeout: 300000 });
  return result.trim();
}

function transcribeChunked(audioPath, lang, apiKey) {
  // 简单方案：用 PowerShell 按字节分片（不完美但能用）
  // 更好的方案需要 ffmpeg
  console.log(`  ⚠️ 文件过大且无 ffmpeg，无法分片转录。请安装 ffmpeg。`);
  console.log(`  尝试直接上传（可能失败）...`);
  try {
    return callGroqWhisper(audioPath, lang, apiKey);
  } catch (e) {
    console.log(`  转录失败: ${e.message}`);
    return `[转录失败: 文件过大(${(fs.statSync(audioPath).size/1024/1024).toFixed(0)}MB)，需要安装 ffmpeg 来压缩音频]`;
  }
}

// 检查新一期
function check() {
  const config = loadConfig();
  const state = loadState();
  let newCount = 0;

  console.log('\n🔍 检查播客更新...\n');

  for (const podcast of config.podcasts) {
    console.log(`📻 ${podcast.name}`);
    try {
      const items = fetchRSS(podcast.feed);
      for (const item of items) {
        const key = `${podcast.name}::${item.title}`;
        if (state.processed[key]) {
          console.log(`  ✅ 已处理: ${item.title}`);
          continue;
        }
        const alreadyPending = state.pending.some(p => p.key === key);
        if (alreadyPending) {
          console.log(`  ⏳ 待处理: ${item.title}`);
          continue;
        }
        console.log(`  🆕 新一期: ${item.title} (${item.pubDate})`);
        state.pending.push({
          key,
          podcast: podcast.name,
          title: item.title,
          pubDate: item.pubDate,
          audioUrl: item.audioUrl,
          lang: podcast.lang
        });
        newCount++;
      }
    } catch (e) {
      console.log(`  ❌ 获取失败: ${e.message}`);
    }
    console.log('');
  }

  saveState(state);
  console.log(`共发现 ${newCount} 个新一期，${state.pending.length} 个待处理\n`);
  return newCount;
}

// 处理待转录的
function processOne() {
  const config = loadConfig();
  const state = loadState();

  if (state.pending.length === 0) {
    console.log('没有待处理的播客。');
    return null;
  }

  const item = state.pending[0];
  console.log(`\n🎙️ 处理: ${item.podcast} - ${item.title}\n`);

  // 1. 下载音频
  const safeTitle = item.title.replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, '_').slice(0, 60);
  const audioPath = path.join(AUDIO_DIR, `${safeTitle}.mp3`);

  if (!fs.existsSync(audioPath)) {
    if (!item.audioUrl) {
      console.log('  ❌ 没有音频链接，跳过');
      state.pending.shift();
      state.processed[item.key] = { status: 'no_audio', time: new Date().toISOString() };
      saveState(state);
      return null;
    }
    downloadFile(item.audioUrl, audioPath);
  } else {
    console.log(`  音频已存在，跳过下载`);
  }

  // 2. 转录
  const transcriptPath = path.join(TRANSCRIPT_DIR, `${safeTitle}.txt`);
  let transcript;

  if (fs.existsSync(transcriptPath)) {
    console.log(`  转录文件已存在，跳过`);
    transcript = fs.readFileSync(transcriptPath, 'utf8');
  } else {
    transcript = transcribeWithGroq(audioPath, item.lang, config.groq_api_key);
    fs.writeFileSync(transcriptPath, transcript);
    console.log(`  转录完成: ${transcript.length} 字符`);
  }

  // 3. 更新状态
  state.pending.shift();
  state.processed[item.key] = {
    status: 'done',
    time: new Date().toISOString(),
    transcriptPath,
    audioPath,
    charCount: transcript.length
  };
  saveState(state);

  console.log(`\n✅ 完成: ${item.title}`);
  return { ...item, transcript: transcript.slice(0, 500) + '...', transcriptPath };
}

// 列出已处理的
function list() {
  const state = loadState();
  console.log('\n📋 已处理的播客:\n');
  for (const [key, info] of Object.entries(state.processed)) {
    const [podcast, title] = key.split('::');
    console.log(`  ${podcast} | ${title} | ${info.status} | ${info.time || 'N/A'}`);
  }
  console.log(`\n⏳ 待处理: ${state.pending.length} 个\n`);
}

// CLI
const cmd = process.argv[2];
switch (cmd) {
  case 'check': check(); break;
  case 'process': processOne(); break;
  case 'list': list(); break;
  default:
    console.log('用法:');
    console.log('  node podcast.js check    — 检查新一期');
    console.log('  node podcast.js process  — 处理一个待转录的');
    console.log('  node podcast.js list     — 列出已处理的');
}
