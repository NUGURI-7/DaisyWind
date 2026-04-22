<template>
  <div class="flex h-full w-full">
    <!-- 编辑区域（充满剩余空间） -->
    <div class="flex-1 flex min-w-0 @container overflow-hidden">
      <!-- 主列（含 toolbar） -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <!-- Toolbar -->
        <div
          v-if="store.selectedId"
          class="h-14 shrink-0 flex items-center px-6 gap-2 border-b border-border/40"
        >
          <span class="text-sm font-semibold text-foreground truncate flex-1">
            {{ store.notesById[store.selectedId]?.title || 'Untitled' }}
          </span>

          <!-- 状态指示器区 -->
          <div class="flex items-center gap-1.5 text-xs font-medium shrink-0 h-full">
            <transition name="fade">
              <span v-if="store.saving === 'saving'" class="flex items-center gap-1.5 text-info">
                <PhSpinner :size="14" class="animate-spin" />
                Saving...
              </span>
            </transition>
            <transition name="fade">
              <span
                v-if="store.saving === 'saved'"
                class="flex items-center gap-1.5 text-success animate-[fadeOut_2s_ease-out_forwards]"
              >
                <PhCheckCircle :size="14" class="animate-[popIn_0.35s_ease]" />
                Saved
              </span>
            </transition>
            <transition name="fade">
              <span
                v-if="store.saving === 'error'"
                class="flex items-center gap-1.5 text-destructive"
              >
                Save failed
              </span>
            </transition>
          </div>

          <!-- (删除按钮已经移到侧边栏，这里保留一个 AI Toggle 面板按钮) -->
          <button
            @click="aiVisible = !aiVisible"
            class="hidden md:flex items-center justify-center size-7 rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 shrink-0 cursor-pointer"
            :class="
              aiVisible
                ? 'text-primary bg-primary/10 hover:bg-primary/20'
                : 'text-muted-foreground/80 hover:text-foreground hover:bg-muted'
            "
            aria-label="Toggle AI panel"
          >
            <PhLayout :size="20" />
          </button>
        </div>

        <!-- 编辑容器主体 -->
        <div
          class="flex-1 overflow-y-auto py-8 lg:px-24 md:px-12 px-4 min-w-0 flex flex-col [scrollbar-gutter:stable]"
        >
          <div v-if="store.selectedId" class="flex-1 max-w-4xl mx-auto w-full">
            <div ref="editorRef" class="h-full animate-[editorIn_0.35s_ease_both]" />
          </div>
          <div
            v-else
            class="flex flex-col items-center justify-center h-full text-center px-4 animate-[editorIn_0.4s_ease_both]"
          >
            <div
              class="flex items-center justify-center size-16 rounded-full bg-muted/50 text-foreground/20 mb-4 animate-[float_3s_ease-in-out_infinite]"
            >
              <PhNoteBlank :size="32" weight="light" />
            </div>
            <h3 class="text-sm font-medium text-foreground/70 mb-1">No Note Selected</h3>
            <p class="text-xs text-muted-foreground/70 max-w-xs mb-6 leading-relaxed">
              Choose a note from the sidebar or create a new one to start writing.
            </p>
            <button
              @click="createNote"
              class="flex items-center h-9 px-4 gap-2 rounded-md bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 cursor-pointer"
            >
              <PhPlus :size="16" />
              Create New Note
            </button>
          </div>
        </div>
      </div>

      <!-- AI 面板 (侧边滑出) -->
      <div
        class="hidden md:block shrink-0 overflow-hidden transition-[width] duration-300"
        :class="aiVisible ? 'w-100' : 'w-0'"
      >
        <div class="w-100 h-full border-l border-border bg-muted/10"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, watch, nextTick, onMounted } from 'vue'
import { Crepe } from '@milkdown/crepe'
import mediaApi from '@/api/media'
import { uploadConfig, upload } from '@milkdown/kit/plugin/upload'
import type { Node } from '@milkdown/kit/prose/model'
import type { Ctx } from '@milkdown/kit/ctx'
import { toast } from 'vue-sonner'
import { useBreakpoints } from '@vueuse/core'
import '@milkdown/crepe/theme/common/style.css'
import '@milkdown/crepe/theme/frame.css'
import { PhPlus, PhLayout, PhNoteBlank, PhSpinner, PhCheckCircle } from '@phosphor-icons/vue'
import { useNoteStore } from '@/stores/notes'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const store = useNoteStore()
// 定义断点（和全局保持一致，lg: 1024px）
const breakpoints = useBreakpoints({
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
})

// 判断当前是否大于等于 lg (1024px)
const isLargeScreen = breakpoints.greaterOrEqual('lg')
// 初始状态：如果是大屏，默认展开 (true)；如果是小屏，默认收起 (false)
const aiVisible = ref(isLargeScreen.value)
watch(isLargeScreen, (isLarge) => {
  aiVisible.value = isLarge
})

const editorRef = ref<HTMLElement>()
const showDeleteDialog = ref(false)

let crepe: Crepe | null = null
let pollTimer: ReturnType<typeof setInterval> | null = null

// ── 工具函数 ───────────────────────────────────────────────
const formatDate = (iso?: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

/** 去除 HTML 标签，用于安全展示 preview 文本 */
const stripHtml = (html?: string) => {
  if (!html) return ''
  const doc = new DOMParser().parseFromString(html, 'text/html')
  return doc.body.textContent?.trim() || ''
}

// ── 代码块交互（不变）─────────────────────────────────────

const handleEditorKeydown = (e: KeyboardEvent) => {
  if (['ArrowDown', 'ArrowUp', 'Enter'].includes(e.key)) {
    const active = document.activeElement as HTMLElement
    const picker = active?.closest('.language-picker')
    if (picker) {
      const focusable = Array.from(
        picker.querySelectorAll<HTMLElement>('input.search-input, li.language-list-item'),
      )
      if (!focusable.length) return

      const currentIndex = focusable.indexOf(active)

      if (e.key === 'ArrowDown') {
        e.preventDefault()
        const nextIndex = (currentIndex + 1) % focusable.length
        focusable[nextIndex]?.focus()
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        const prevIndex = (currentIndex - 1 + focusable.length) % focusable.length
        focusable[prevIndex]?.focus()
      } else if (e.key === 'Enter' && active.tagName.toLowerCase() === 'input') {
        e.preventDefault()
        const firstItem = focusable.find((el) => el.tagName.toLowerCase() === 'li')
        if (firstItem) {
          firstItem.click()
        }
      }
    }
  }
}

const handleEditorClick = (e: Event) => {
  const target = e.target as Element

  const tools = target.closest<HTMLElement>('.milkdown-code-block .tools')
  if (
    tools &&
    !target.closest('.language-button') &&
    !target.closest('.language-picker') &&
    !target.closest('.copy-button')
  ) {
    const block = tools.closest<HTMLElement>('.milkdown-code-block')
    if (block)
      block.setAttribute('data-collapsed', block.getAttribute('data-collapsed') === '1' ? '0' : '1')
    return
  }

  const copyBtn = target.closest<HTMLElement>('.copy-button')
  if (copyBtn && !copyBtn.hasAttribute('data-copied')) {
    copyBtn.setAttribute('data-copied', '1')
    setTimeout(() => copyBtn.removeAttribute('data-copied'), 2000)
  }
}

// ── Editor ────────────────────────────────────────────────
const destroyEditor = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  editorRef.value?.removeEventListener('click', handleEditorClick)
  editorRef.value?.removeEventListener('keydown', handleEditorKeydown)
  if (crepe) {
    crepe.destroy()
    crepe = null
  }
}

const initEditor = async (content: string) => {
  destroyEditor()
  if (!editorRef.value) return
  editorRef.value.innerHTML = ''

  const handleUpload = async (file: File) => {
    try {
      const { data } = await mediaApi.getPresignedUrl(file.name, file.type)
      if (!data) throw new Error('获取签名失败')

      const { upload_url, public_url } = data

      const res = await fetch(upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
      })
      if (!res.ok) throw new Error('oss error')
      return public_url
    } catch (error) {
      console.error('Image upload failed:', error)
      toast.error('图片上传失败')
      throw error // 把错误抛回去，Crepe 会结束上传 loading
    }
  }

  crepe = new Crepe({
    root: editorRef.value,
    defaultValue: content,
    featureConfigs: {
      [Crepe.Feature.ImageBlock]: {
        onUpload: handleUpload,
        inlineOnUpload: handleUpload,
        blockOnUpload: handleUpload,
      },
    },
  })

  crepe.editor.use(upload).config((ctx: Ctx) => {
    ctx.update(uploadConfig.key, (prev) => ({
      ...prev,
      // 粘贴或拖拽文件时，Milkdown 会把所有的 File 对象扔给 uploader
      uploader: async (files: FileList, schema: any) => {
        const nodes: Node[] = []
        for (let i = 0; i < files.length; i++) {
          const file = files[i]

          try {
            const url = await handleUpload(file!)

            if (file?.type.startsWith('image/')) {
              nodes.push(schema.nodes.image.createAndFill({ src: url, alt: file.name }) as Node)
            } else {
              const textNode = schema.text(file?.name)
              const linkMark = schema.marks.link.create({ herf: url, title: file?.name })
              nodes.push(textNode.mark([linkMark]) as Node)
            }
          } catch (e) {
            console.error('Drag/Paste upload failed', e)
          }
        }
        return nodes
      },
    }))
  })

  await crepe.create()
  editorRef.value.querySelector<HTMLElement>('.ProseMirror')?.setAttribute('spellcheck', 'false')
  editorRef.value.addEventListener('click', handleEditorClick)
  editorRef.value.addEventListener('keydown', handleEditorKeydown)

  let lastMd = content
  pollTimer = setInterval(async () => {
    if (!crepe || !store.selectedId) return
    const md = await crepe.getMarkdown()
    if (md !== lastMd) {
      lastMd = md
      store.save(store.selectedId, md)
    }
  }, 800)
}

// ── Note actions ───────────────────────────────────────────
const selectNote = async (uuid: string) => {
  if (uuid === store.selectedId) return
  await store.flush()
  store.selectedId = uuid
  router.push({ query: { id: uuid } })
}

const createNote = async () => {
  const newId = await store.create()

  if (newId) {
    router.push({ query: { id: newId } }) // 更新地址栏
  }
}

const confirmDelete = () => (showDeleteDialog.value = true)

const doDelete = async () => {
  showDeleteDialog.value = false
  if (store.selectedId) await store.remove(store.selectedId)
}

// ── 监听 selectedId，加载内容并初始化编辑器 ───────────────
watch(
  () => store.selectedId,
  async (uuid) => {
    destroyEditor()
    if (!uuid) return
    const note = store.notesById[uuid]
    if (note?.content !== undefined) {
      await nextTick()
      initEditor(note.content)
    } else {
      await store.fetchOne(uuid)
      await nextTick()
      const loaded = store.notesById[uuid]
      if (loaded?.content !== undefined) initEditor(loaded.content)
    }
  },
  { immediate: true },
)

onMounted(async () => {
  await store.fetchList()

  const idFromUrl = route.query.id

  if (idFromUrl && typeof idFromUrl === 'string') {
    store.selectedId = idFromUrl
  } else {
    store.selectedId = null
  }
})

watch(
  () => route.query.id,
  (newId) => {
    if (newId && typeof newId === 'string') {
      store.selectedId = newId
    } else {
      store.selectedId = null
    }
  },
)

onBeforeUnmount(() => {
  store.flush()
  destroyEditor()
})
</script>

<style>
/* ── Milkdown / Crepe 主题覆盖 ── */
.milkdown {
  --crepe-color-background: #f4f3ee;
  --crepe-color-on-background: var(--foreground);
  --crepe-color-surface: #ece9e3;
  --crepe-color-surface-low: #e2dfd9;
  --crepe-color-on-surface: var(--foreground);
  --crepe-color-outline: var(--foreground);
  --crepe-color-primary: var(--primary);
  --crepe-color-hover: #e2dfd9;
  --crepe-color-selected: #d8d5cf;
  --crepe-font-default: ui-sans-serif, system-ui, sans-serif;
  --crepe-font-title: ui-sans-serif, system-ui, sans-serif;
  height: 100% !important;
  min-height: 100% !important;
  background: #f4f3ee !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* ── Crepe frame 主题默认 padding: 60px 120px，覆盖为合理值 ── */
.milkdown .ProseMirror {
  padding: 48px clamp(20px, 6%, 64px) !important;
}

/* ── 代码块：gutter 背景与编辑器统一 ── */
.milkdown .cm-gutters {
  background-color: inherit !important;
  border-right: none !important;
}

/* ── 当前行高亮：去掉行号变黑 ── */
.milkdown .cm-activeLineGutter {
  background-color: transparent !important;
  color: inherit !important;
}
.milkdown .cm-activeLine {
  background-color: transparent !important;
}

/* ── 隐藏代码块自动补全下拉框（保留括号自动闭合） ── */
.milkdown .cm-tooltip-autocomplete {
  display: none !important;
}

/* ── 图标颜色：milkdown-icon ── */
.milkdown .milkdown-icon svg,
.milkdown .milkdown-icon svg * {
  fill: var(--foreground) !important;
  color: var(--foreground) !important;
}

/* ── 图标颜色：浮层组件（block-handle / toolbar / slash 等）── */
.milkdown > *:not(.ProseMirror) svg,
.milkdown > *:not(.ProseMirror) svg * {
  fill: var(--foreground) !important;
  color: var(--foreground) !important;
}

/* ── 列表 label 颜色继承 ── */
.milkdown .milkdown-list-item-block .label-wrapper {
  color: var(--foreground) !important;
}

/* ── 代码块头部：始终可见，无背景 ── */
.milkdown .milkdown-code-block .tools .tools-button-group button {
  opacity: 1 !important;
}
.milkdown .milkdown-code-block .tools .language-button {
  opacity: 1 !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* ── 代码块头部：整行可点击折叠 ── */
.milkdown .milkdown-code-block .tools {
  cursor: pointer;
}
/* 排除语言/复制按钮自身 hover */
.milkdown .milkdown-code-block .tools .language-button,
.milkdown .milkdown-code-block .tools .copy-button {
  cursor: pointer;
}

/* ── Copy 按钮样式 ── */
.milkdown .copy-button {
  font-size: 0 !important;
  gap: 0 !important;
  padding: 4px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: transparent !important;
  border: none;
  cursor: pointer;
  color: var(--foreground);
  border-radius: 4px;
}
.milkdown .copy-button:hover {
  background: var(--crepe-color-hover) !important;
}
.milkdown .copy-button:active {
  background: var(--crepe-color-selected) !important;
}

/* ── Copy 按钮：去掉文字，换 Phosphor PhCopy 图标 ── */
.milkdown .copy-button .milkdown-icon {
  display: none !important;
}
.milkdown .copy-button::before {
  content: '';
  display: block;
  width: 14px;
  height: 14px;
  background-color: currentColor;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32Zm-56,176H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32Zm-56,176H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  transition: mask 0s;
}
/* 复制成功：PhCheck 图标 + 绿色 */
.milkdown .copy-button[data-copied]::before {
  background-color: oklch(0.65 0.15 145);
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M229.66,77.66l-128,128a8,8,0,0,1-11.32,0l-56-56a8,8,0,0,1,11.32-11.32L96,188.69,218.34,66.34a8,8,0,0,1,11.32,11.32Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
}

/* ── 折叠 caret：tools-button-group::before，展开=Up，折叠=Down ── */
.milkdown .milkdown-code-block .tools-button-group::before {
  content: '';
  display: block;
  width: 14px;
  height: 14px;
  align-self: center;
  background-color: var(--foreground);
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M213.66,165.66a8,8,0,0,1-11.32,0L128,91.31,53.66,165.66a8,8,0,0,1-11.32-11.32l80-80a8,8,0,0,1,11.32,0l80,80A8,8,0,0,1,213.66,165.66Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M213.66,165.66a8,8,0,0,1-11.32,0L128,91.31,53.66,165.66a8,8,0,0,1-11.32-11.32l80-80a8,8,0,0,1,11.32,0l80,80A8,8,0,0,1,213.66,165.66Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  pointer-events: none;
}
.milkdown .milkdown-code-block[data-collapsed='1'] .tools-button-group::before {
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M213.66,101.66l-80,80a8,8,0,0,1-11.32,0l-80-80A8,8,0,0,1,53.66,90.34L128,164.69l74.34-74.35a8,8,0,0,1,11.32,11.32Z'/%3E%3C/svg%3E")
    no-repeat center / contain;
}

/* ── 代码块折叠/展开平滑过渡 ── */
.milkdown .milkdown-code-block .codemirror-host {
  max-height: 2000px;
  opacity: 1;
  overflow: hidden;
  transition:
    max-height 0.3s ease,
    opacity 0.2s ease;
}
.milkdown .milkdown-code-block[data-collapsed='1'] .codemirror-host {
  max-height: 0 !important;
  opacity: 0 !important;
  transition:
    max-height 0.25s ease,
    opacity 0.15s ease;
}

/* ── Blockquote 左侧竖条颜色 ── */
.milkdown .ProseMirror blockquote::before {
  background-color: oklch(0.85 0.03 73) !important;
}

/* ── 代码块无内边距 ── */
.milkdown .milkdown-code-block {
  padding: 0 !important;
  margin: 4px 0 !important;
}

/* ── New Note 按钮：流动边框 hover 动效 ── */
@property --nna {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

.new-note-wrap {
  position: relative;
  border-radius: var(--radius-field, 0.5rem);
}

.new-note-wrap::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 2px;
  border-radius: inherit;
  background: conic-gradient(
    from var(--nna),
    transparent 0%,
    var(--primary) 25%,
    color-mix(in oklch, var(--primary) 60%, white) 50%,
    transparent 70%
  );
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.35s ease;
  animation: nna-spin 1.8s linear infinite paused;
  pointer-events: none;
}

.new-note-wrap:hover::before {
  opacity: 1;
  animation-play-state: running;
}

@keyframes nna-spin {
  to {
    --nna: 360deg;
  }
}

/* ── Block hover：背景变色 ── */
.milkdown .ProseMirror > * {
  border-radius: 4px;
  transition: background-color 0.15s;
}
.milkdown .ProseMirror > *:hover {
  background-color: var(--muted);
}

/* ── Block handle：缩小图标 ── */
.milkdown .milkdown-block-handle .operation-item {
  width: 20px !important;
  height: 20px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.milkdown .milkdown-block-handle .operation-item .milkdown-icon svg {
  width: 14px !important;
  height: 14px !important;
}

/* ── CodeMirror 纯文本颜色 ── */
.milkdown .cm-content {
  color: var(--foreground);
}

/* ── CodeMirror 语法高亮 — Catppuccin Latte ── */
.milkdown .cm-editor {
  /* keyword: if / else / return / const / let — 薰衣草紫 Mauve */
  & .tok-keyword {
    color: #8839ef !important;
  }
  /* string: "hello" / 'world' — 绿色 Green */
  & .tok-string,
  & .tok-string2 {
    color: #40a02b !important;
  }
  /* number: 42 / 3.14 — 蜜桃色 Peach */
  & .tok-number {
    color: #fe640b !important;
  }
  /* bool / null: true / false / null — 蜜桃色 Peach */
  & .tok-bool,
  & .tok-null {
    color: #fe640b !important;
  }
  /* comment: // ... / /* ... */
  — 灰色 Overlay0 */ & .tok-comment {
    color: #9ca0b0 !important;
    font-style: italic;
  }
  /* propertyName: JSON key / object key — 蓝色 Blue */
  & .tok-propertyName {
    color: #1e66f5 !important;
  }
  /* typeName: class name / type — 黄色 Yellow */
  & .tok-typeName {
    color: #df8e1d !important;
  }
  /* function / definition name — 蓝色 Blue */
  & .tok-definition,
  & .tok-function {
    color: #1e66f5 !important;
  }
  /* variable — 正文色 Text */
  & .tok-variableName {
    color: #4c4f69 !important;
  }
  /* special variable: this / self — 红色 Red */
  & .tok-variableName.tok-special {
    color: #d20f39 !important;
  }
  /* operator: + - = === — Subtext0 偏暗 */
  & .tok-operator {
    color: #179299 !important;
  }
  /* punctuation: {} [] () , ; — Overlay1 */
  & .tok-punctuation {
    color: #8c8fa1 !important;
  }
  /* tag name (HTML/XML) — 红色 Maroon */
  & .tok-tagName {
    color: #e64553 !important;
  }
  /* attribute name (HTML) — 黄色 Yellow */
  & .tok-attributeName {
    color: #df8e1d !important;
  }
  /* attribute value (HTML) — 绿色 Green */
  & .tok-attributeValue {
    color: #40a02b !important;
  }
  /* meta / preprocessor — 粉色 Pink */
  & .tok-meta {
    color: #ea76cb !important;
  }
  /* heading (Markdown) — 红色 Red + bold */
  & .tok-heading {
    color: #d20f39 !important;
    font-weight: 600;
  }
  /* link (URL) — 蓝色 Sapphire */
  & .tok-link,
  & .tok-url {
    color: #209fb5 !important;
  }
  /* atom (CSS value, special literal) — 蜜桃 Peach */
  & .tok-atom {
    color: #fe640b !important;
  }
  /* regexp — 粉色 Pink */
  & .tok-regexp {
    color: #ea76cb !important;
  }
  /* selection / cursor */
  & .cm-selectionBackground {
    background-color: #bcc0ccb0 !important;
  }
  & .cm-cursor {
    border-left-color: #dc8a78 !important;
  }
}

/* Vue transition 过渡类 */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-2px);
}

/* ── 空状态图标呼吸浮动 ── */
@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* ── Saved checkmark 弹跳 ── */
@keyframes popIn {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  60% {
    transform: scale(1.15);
    opacity: 1;
  }
  100% {
    transform: scale(1);
  }
}

/* ── 编辑器切换淡入上浮 ── */
@keyframes editorIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 列表项错开入场 ── */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 延迟淡出动画（给 Saved 用的） */
@keyframes fadeOut {
  0%,
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}
</style>
