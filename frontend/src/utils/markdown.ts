// frontend/src/utils/markdown.ts
import MarkdownIt, { type Options } from 'markdown-it'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'

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
  const lang = info.split(/\s+/g)[0] || ''
  const rawCode = token.content.replace(/\n+$/, '')

  let highlighted = ''
  if (lang && hljs.getLanguage(lang)) {
    try {
      highlighted = hljs.highlight(rawCode, { language: lang, ignoreIllegals: true }).value
    } catch {
      highlighted = md.utils.escapeHtml(rawCode)
    }
  } else {
    highlighted = md.utils.escapeHtml(rawCode)
  }

  const displayLang = lang ? lang.toUpperCase() : 'CODE'
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
    ADD_ATTR: ['target', 'data-code'],
  })

  return safeHtml
}
