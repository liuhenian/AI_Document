'use strict';

/*
 * Code Reader — 本地自建插件
 * 目的：让 Obsidian 能直接“打开并读取”源码/文本文件（点文件列表里的 .py 就出内容）。
 * 做法：把这些扩展名注册到自定义的只读视图，视图内部把文件内容包成
 *       一个 markdown 代码围栏，交给 Obsidian 自己的渲染器（MarkdownRenderer），
 *       于是语法高亮、主题配色、复制按钮全部复用原生能力，不引入任何外部依赖。
 * 特点：零网络请求、只读（无法在本视图里误改源码）、大文件走渲染管线不卡编辑器。
 */

const { Plugin, FileView, MarkdownRenderer } = require('obsidian');

const VIEW_TYPE = 'code-reader-view';

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

    const ext = (file.extension || '').toLowerCase();
    const lang = EXT_TO_LANG[ext] || ext || 'text';
    const fence = '`'.repeat(Math.max(3, longestBacktickRun(code) + 1));
    const markdown = fence + lang + '\n' + code + '\n' + fence;

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
