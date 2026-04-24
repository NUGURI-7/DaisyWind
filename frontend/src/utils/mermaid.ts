import type { MermaidConfig } from 'mermaid'

type MermaidApi = typeof import('mermaid').default

let mermaidPromise: Promise<MermaidApi> | null = null

function fromBase64(b64: string): string {
  const binary = atob(b64)
  const bytes = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i)
  }
  return new TextDecoder().decode(bytes)
}

/**
 * 懒加载 mermaid：首次调用时动态 import 并初始化
 * 后续调用复用同一个 Promise，避免重复加载
 */
function loadMermaid(): Promise<MermaidApi> {
  if (mermaidPromise) return mermaidPromise

  mermaidPromise = import('mermaid').then((mod) => {
    const mermaid = mod.default
    const config: MermaidConfig = {
      startOnLoad: false,
      theme: 'default', // 保持不动
      securityLevel: 'strict',
      fontFamily: 'inherit',
      themeVariables: {
        edgeLabelBackground: '#ffffff', // 或 'transparent'
      },
    }
    mermaid.initialize(config)
    return mermaid
  })

  return mermaidPromise
}

let renderSeq = 0

/**
 * 渲染单个 Mermaid 容器
 * - 读 data-mermaid-source 取源码
 * - 调 mermaid.render() 生成 SVG
 * - 替换容器内容，并把 data-mermaid-rendered 标记为 1
 * - 出错时展示错误信息
 */
export async function renderMermaidContainer(container: HTMLElement): Promise<void> {
  if (container.dataset.mermaidRendered === '1') return

  // ↓↓↓ 替换点：把原来的 const source = container.dataset.mermaidSource 换成下面 ↓↓↓
  const encoded = container.dataset.mermaidSource
  if (!encoded) return

  let source: string
  try {
    source = fromBase64(encoded)
  } catch {
    return
  }
  // ↑↑↑ 到这里结束 ↑↑↑

  try {
    const mermaid = await loadMermaid()
    const id = `mermaid-${Date.now()}-${renderSeq++}`
    const { svg } = await mermaid.render(id, source)

    container.innerHTML = svg
    container.dataset.mermaidRendered = '1'
    container.classList.remove('items-center', 'justify-center', 'min-h-[120px]')
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    container.innerHTML = `
      <div class="flex flex-col gap-1 text-sm text-destructive p-2">
        <div class="font-medium">图表渲染失败</div>
        <div class="text-xs font-mono whitespace-pre-wrap break-all opacity-80">${escapeHtml(message)}</div>
      </div>
    `
    container.dataset.mermaidRendered = '1'
    container.classList.remove('items-center', 'justify-center', 'min-h-[120px]')
  }
}

/**
 * 扫描根节点下所有未渲染的 Mermaid 容器，并发渲染
 */
export async function renderAllMermaid(root: HTMLElement): Promise<void> {
  const containers = root.querySelectorAll<HTMLElement>(
    '.mermaid-container[data-mermaid-rendered="0"]',
  )
  if (containers.length === 0) return

  await Promise.all(Array.from(containers).map(renderMermaidContainer))
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
