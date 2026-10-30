'use strict';

/*
 * Code Reader — 本地自建插件
 * 目的：让 Obsidian 能直接“打开并读取”源码/文本文件（点文件列表里的 .py 就出内容）。
 * 做法：把这些扩展名注册到自定义的只读视图，视图内部把文件内容包成
 *       一个 markdown 代码围栏，交给 Obsidian 自己的渲染器（MarkdownRenderer），
 *       于是语法高亮、主题配色、复制按钮全部复用原生能力，不引入任何外部依赖。
 * 特点：零网络请求、只读（无法在本视图里误改源码）。
 *
 * 2026-10-29 修复：加大小保护。
 *   起因：打开 _附件-977条工单打标结果.json（718 KB / 20,691 行）时，
 *   整个文件被塞进一个代码围栏，Obsidian 的代码块渲染器要逐行高亮两万行，
 *   渲染进程卡死（Windows 事件日志不会记录渲染进程卡死，所以查不到崩溃痕迹）。
 *   现在超限只渲染前 MAX_LINES 行，并给出明确提示。
 */

const { Plugin, FileView, MarkdownRenderer } = require('obsidian');

const VIEW_TYPE = 'code-reader-view';

// 渲染上限：超过就截断预览，不把整个文件塞进代码块
const MAX_LINES = 2000;        // 最多渲染行数
const MAX_CHARS = 200000;      // 最多渲染字符数（约 200 KB）
const MAX_LINE_CHARS = 4000;   // 单行最多渲染字符数（防超长单行行宽爆炸）

// 扩展名 -> 代码围栏语言名。没列到的扩展名会原样当语言名传下去，Obsidian 不认识就用纯文本。
const EXT_TO_LANG = {
  py: 'python',
  pyw: 'python',
  js: 'javascript',
  mjs: 'javascript',
  cjs: 'javascript',
  jsx: 'jsx',
  ts: 'typescript',
  tsx: 'tsx',
  java: 'java',
  go: 'go',
  rs: 'rust',
  c: 'c',
  h: 'c',
  cc: 'cpp',
  cpp: 'cpp',
  hpp: 'cpp',
  cs: 'csharp',
  rb: 'ruby',
  php: 'php',
  lua: 'lua',
  sh: 'bash',
  bash: 'bash',
  zsh: 'bash',
  ps1: 'powershell',
  bat: 'batch',
  cmd: 'batch',
  sql: 'sql',
  yaml: 'yaml',
  yml: 'yaml',
  toml: 'toml',
  ini: 'ini',
  conf: 'ini',
  cfg: 'ini',
  json: 'json',
  xml: 'xml',
  html: 'html',
  css: 'css',
  scss: 'scss',
  less: 'less',
  kt: 'kotlin',
  swift: 'swift',
  vue: 'vue',
  log: 'text',
  txt: 'text',
  csv: 'csv',
  service: 'ini',
  env: 'ini',
  properties: 'ini',
};

/**
 * 找出文本里最长的一段连续反引号，围栏要比它长，否则会把内容截断。
 */
function longestBacktickRun(text) {
  let best = 0;
  let cur = 0;
  for (let i = 0; i < text.length; i++) {
    if (text.charCodeAt(i) === 96) {
      cur++;
      if (cur > best) best = cur;
    } else {
      cur = 0;
    }
  }
  return best;
}

function humanSize(bytes) {
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB';
  if (bytes >= 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return bytes + ' B';
}

/**
 * 按行数与字符数双阈值截断，返回 { text, truncated, shownLines, totalLines, reason }
 */
function clampContent(code) {
  const totalLines = code.length ? code.split('\n').length : 0;
  const chars = code.length;

  if (totalLines <= MAX_LINES && chars <= MAX_CHARS) {
    // 顺手处理超长单行（几 KB 一行也会让排版与行宽计算变慢）
    let overlong = false;
    const lines = code.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].length > MAX_LINE_CHARS) {
        lines[i] = lines[i].slice(0, MAX_LINE_CHARS) + ' …（本行过长，已截断）';
        overlong = true;
      }
    }
    return {
      text: overlong ? lines.join('\n') : code,
      truncated: overlong,
      shownLines: totalLines,
      totalLines: totalLines,
      reason: overlong ? '单行过长' : '',
    };
  }

  const lines = code.split('\n');
  const kept = [];
  let used = 0;
  for (let i = 0; i < lines.length && kept.length < MAX_LINES; i++) {
    let line = lines[i];
    if (line.length > MAX_LINE_CHARS) line = line.slice(0, MAX_LINE_CHARS) + ' …（本行过长，已截断）';
    if (used + line.length > MAX_CHARS) break;
    kept.push(line);
    used += line.length + 1;
  }

  return {
    text: kept.join('\n'),
    truncated: true,
    shownLines: kept.length,
    totalLines: totalLines,
    reason: kept.length < MAX_LINES ? '字符数超限' : '行数超限',
  };
}

class CodeReaderView extends FileView {
  constructor(leaf) {
    super(leaf);
    this.navigation = true;
    this.allowNoFile = false;
  }

  getViewType() {
    return VIEW_TYPE;
  }

  getIcon() {
    return 'file-code';
  }

  getDisplayText() {
    return this.file ? this.file.name : 'Code Reader';
  }

  async onLoadFile(file) {
    this.contentEl.empty();
    this.contentEl.addClass('code-reader-view');

    let code;
    try {
      code = await this.app.vault.read(file);
    } catch (err) {
      this.contentEl.createEl('p', {
        cls: 'code-reader-error',
        text: '读取失败：' + (err && err.message ? err.message : String(err)),
      });
      return;
    }

    // 视图可能已经被切走（快速连点文件），避免往旧视图里渲染
    if (this.file !== file) return;

    const clamped = clampContent(code);
    if (clamped.truncated) {
      const notice = this.contentEl.createDiv({ cls: 'code-reader-notice' });
      notice.createEl('strong', { text: '仅显示预览片段' });
      notice.createEl('div', {
        text:
          '文件共 ' + clamped.totalLines.toLocaleString() + ' 行 / ' + humanSize(code.length) +
          '，已渲染前 ' + clamped.shownLines.toLocaleString() + ' 行（' + clamped.reason +
          '）。完整内容请右键该文件 → 在默认应用中打开。',
      });
    }

    const ext = (file.extension || '').toLowerCase();
    const lang = EXT_TO_LANG[ext] || ext || 'text';
    const fence = '`'.repeat(Math.max(3, longestBacktickRun(clamped.text) + 1));
    const markdown = fence + lang + '\n' + clamped.text + '\n' + fence;

    // 挂上 markdown-preview-view + markdown-rendered，直接复用阅读模式的排版与代码高亮
    const body = this.contentEl.createDiv({
      cls: 'markdown-preview-view markdown-rendered code-reader-body',
    });
    try {
      await MarkdownRenderer.render(this.app, markdown, body, file.path, this);
    } catch (err) {
      body.empty();
      body.createEl('p', {
        cls: 'code-reader-error',
        text: '渲染失败：' + (err && err.message ? err.message : String(err)),
      });
    }
  }

  async onUnloadFile() {
    this.contentEl.empty();
  }
}

module.exports = class CodeReaderPlugin extends Plugin {
  async onload() {
    this.registerView(VIEW_TYPE, (leaf) => new CodeReaderView(leaf));
    // 只注册文本类扩展名，绝不碰 md / canvas / base / 图片 / pdf
    this.registerExtensions(Object.keys(EXT_TO_LANG), VIEW_TYPE);
  }

  onunload() {
    // registerView / registerExtensions 由 Obsidian 自动回收，这里无需手动清理
  }
};
