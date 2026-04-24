// frontend/src/utils/markdown.ts
import MarkdownIt, { type Options } from 'markdown-it'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'

function toBase64(str: string): string {
  const bytes = new TextEncoder().encode(str)
  let binary = ''
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]!)
  }
  return btoa(binary)
}

// ==========================================
// 代码语言 alias 归一化
// ==========================================

/**
 * AI 输出的非标准语言标签 → hljs 认识的标准名
 * 只列 hljs 原生 alias 不覆盖的情况
 */
const LANG_ALIAS: Record<string, string> = {
  // Shell 家族
  sh: 'bash',
  shell: 'bash',
  zsh: 'bash',
  console: 'bash',
  terminal: 'bash',

  // JS 家族
  node: 'javascript',
  nodejs: 'javascript',
  mjs: 'javascript',
  cjs: 'javascript',

  // TS 家族（hljs 有 ts alias，但大小写变体要兜底）
  'typescript-jsx': 'typescript',
  tsx: 'typescript',
  jsx: 'javascript',

  // Vue / Svelte（hljs 无原生支持，降级到 HTML）
  vue: 'xml',
  svelte: 'xml',
  html: 'xml',

  // 其他常见变体
  yml: 'yaml',
  dockerfile: 'dockerfile', // hljs 原生，但有的写成大写
  md: 'markdown',
  'c++': 'cpp',
  'c#': 'csharp',
  'objective-c': 'objectivec',
  objc: 'objectivec',
  golang: 'go',
  rs: 'rust',
  kt: 'kotlin',
  py3: 'python',
  py2: 'python',
  ipython: 'python',

  // 无语言 / 纯文本
  text: 'plaintext',
  txt: 'plaintext',
  plain: 'plaintext',
  raw: 'plaintext',
}

/**
 * 显示名美化（header 左上角那条标签）
 * 规则：alias 解析后的标准名 → 漂亮的显示名
 */
const DISPLAY_NAME: Record<string, string> = {
  javascript: 'JavaScript',
  typescript: 'TypeScript',
  python: 'Python',
  bash: 'Bash',
  json: 'JSON',
  yaml: 'YAML',
  xml: 'HTML',
  css: 'CSS',
  scss: 'SCSS',
  go: 'Go',
  rust: 'Rust',
  java: 'Java',
  kotlin: 'Kotlin',
  swift: 'Swift',
  cpp: 'C++',
  csharp: 'C#',
  ruby: 'Ruby',
  php: 'PHP',
  sql: 'SQL',
  markdown: 'Markdown',
  dockerfile: 'Dockerfile',
  plaintext: 'Text',
}

/**
 * 把 AI 写的任意语言标签归一化成 hljs 认识的标准名
 */
function normalizeLang(raw: string): string {
  if (!raw) return ''
  const lower = raw.trim().toLowerCase()
  // 先查自定义 alias 表
  if (LANG_ALIAS[lower]) return LANG_ALIAS[lower]
  // 再看 hljs 是否原生认识（包括它内置的 alias）
  if (hljs.getLanguage(lower)) return lower
  // 都不认，返回空字符串（走 fallback）
  return ''
}

/**
 * 根据归一化后的标准名得到 header 显示文本
 */
function prettyLangName(normalized: string, original: string): string {
  if (!normalized) return original ? original.toUpperCase() : 'CODE'
  return DISPLAY_NAME[normalized] || normalized.toUpperCase()
}

// 1. 初始化 markdown-it 实例 (合并 highlight 配置)
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
})

// 完全接管 fence 渲染，不走 options.highlight
md.renderer.rules.fence = function (tokens, idx) {
  const token = tokens[idx]
  if (!token) return ''

  const info = token.info ? token.info.trim() : ''
  const rawLang = info.split(/\s+/g)[0] || ''
  const lang = normalizeLang(rawLang) // ← 归一化
  const rawCode = token.content.replace(/\n+$/, '')

  // ===== Mermaid 特殊分支：不走 hljs，产出占位节点 =====
  if (rawLang.toLowerCase() === 'mermaid') {
    // 用 base64 编码绕开 DOMPurify 对多行属性值的剥除
    const encodedSource = toBase64(rawCode)
    return `<div class="mermaid-container my-4 flex items-center justify-center min-h-[120px] overflow-x-auto rounded-lg border border-border bg-background p-4" data-mermaid-source="${encodedSource}" data-mermaid-rendered="0"><div class="mermaid-loading flex items-center gap-2 text-sm text-brand"><l-helix size="16" stroke="2" speed="2" color="currentColor"></l-helix><span>正在渲染图表...</span></div></div>`
  }

  // ...
  let highlighted = ''
  if (lang) {
    try {
      highlighted = hljs.highlight(rawCode, { language: lang, ignoreIllegals: true }).value
    } catch {
      highlighted = md.utils.escapeHtml(rawCode)
    }
  } else {
    highlighted = md.utils.escapeHtml(rawCode)
  }

  const displayLang = prettyLangName(lang, rawLang) // ← 规范化显示名

  // 下面代码块里 class="language-${lang}" 这行，用 lang（归一化后的）或者 rawLang 都行，
  // 但建议用 rawLang 保留 AI 原始写法，CSS/JS 选择器需要时可根据实际情况选
  const escapedForCopy = md.utils.escapeHtml(rawCode)

  // 注意：整个 return 必须是单行或者所有标签紧贴，不要留缩进空白！
  return `<div class="code-block-wrapper relative group bg-sidebar border border-border rounded-lg overflow-hidden my-4"><div class="code-block-header flex items-center justify-between px-4 py-1.5 bg-muted/50 border-b border-border"><span class="text-xs font-mono text-muted-foreground">${displayLang}</span><button class="copy-btn flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors cursor-pointer" data-code="${escapedForCopy}"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 256 256" class="copy-icon"><path fill="currentColor" d="M216 32H88a8 8 0 0 0-8 8v40H40a8 8 0 0 0-8 8v128a8 8 0 0 0 8 8h128a8 8 0 0 0 8-8v-40h40a8 8 0 0 0 8-8V40a8 8 0 0 0-8-8m-56 176H48V96h112Zm48-48h-32V88a8 8 0 0 0-8-8H96V48h112Z"/></svg><span class="copy-text">Copy</span></button></div><div class="overflow-x-auto p-4 text-sm font-mono leading-relaxed bg-background"><pre><code class="hljs language-${lang}">${highlighted}</code></pre></div></div>`
}

// ... (2. 覆盖默认的链接渲染行为 的代码保持不变) ...

// 3. 核心导出函数
export function renderMarkdown(content: string, isStreaming = false, isUser = false): string {
  if (!content) return ''

  let processedContent = content

  // 处理流式渲染中的 Soft-close
  if (isStreaming) {
    const matches = processedContent.match(/```/g)
    const count = matches ? matches.length : 0
    if (count % 2 !== 0) {
      processedContent += '\n```'
    }
  }

  // 【必改 4】：根据身份差异化动态设置 breaks 规则
  if (isUser) {
    md.set({ breaks: true })
    md.disable(['emphasis'])
  } else {
    md.set({ breaks: false })
    md.enable(['emphasis'])
  }

  const rawHtml = md.render(processedContent)

  const safeHtml = DOMPurify.sanitize(rawHtml, {
    ADD_ATTR: ['target', 'data-code', 'data-mermaid-source', 'data-mermaid-rendered'],
    CUSTOM_ELEMENT_HANDLING: {
      tagNameCheck: /^l-[a-z-]+$/, // 允许所有 l-* 自定义标签（l-ring / l-ping / l-tailspin 等）
      attributeNameCheck: /^(size|stroke|speed|color|bg-opacity)$/, // 允许 ldrs 的属性
      allowCustomizedBuiltInElements: false,
    },
  })

  return safeHtml
}
