<template>
  <div class="flex h-full">

    <!-- 左侧笔记列表 -->
    <div class="w-52 shrink-0 border-r border-base-300 flex flex-col">
      <div class="p-2 border-b border-base-300">
        <button @click="createNote" class="btn btn-ghost btn-sm w-full justify-start gap-2">
          <PhPlus :size="14" />
          New Note
        </button>
      </div>

      <div class="flex-1 overflow-y-auto">
        <button
          v-for="note in notes"
          :key="note.id"
          @click="selectNote(note.id)"
          class="w-full text-left px-3 py-3 hover:bg-base-200 transition-colors border-b border-base-200 cursor-pointer"
          :class="note.id === selectedId ? 'bg-base-200' : ''"
        >
          <div class="text-sm font-medium truncate">{{ note.title || 'Untitled' }}</div>
          <div class="text-xs text-base-content/50 truncate mt-0.5">{{ note.preview }}</div>
          <div class="text-xs text-base-content/30 mt-1">{{ formatDate(note.updatedAt) }}</div>
        </button>

        <div v-if="notes.length === 0" class="px-3 py-6 text-xs text-base-content/40 text-center">
          No notes yet
        </div>
      </div>
    </div>

    <!-- 右侧区域：以此为 container，阈值直接等于书写区域宽度 -->
    <div class="flex flex-1 min-w-0 @container">

      <!-- 编辑区域 -->
      <div class="flex-1 overflow-y-auto py-8 pl-8 pr-8 min-w-0 flex flex-col">
        <div v-if="selectedId" class="flex-1">
          <div ref="editorRef" class="h-full" />
        </div>
        <div v-else class="flex items-center justify-center h-full text-base-content/30 text-sm">
          Select a note or create a new one
        </div>
      </div>

      <!-- AI 面板：右侧区域 ≥ 900px 时显示（即书写区域还有 ~500px 剩余） -->
      <div class="hidden @[900px]:block w-[400px] shrink-0 border-l border-base-200">
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, watch, nextTick } from 'vue'
import { Crepe } from '@milkdown/crepe'
import '@milkdown/crepe/theme/common/style.css'
import '@milkdown/crepe/theme/frame.css'
import { PhPlus } from '@phosphor-icons/vue'

// ── Note / Editor state ────────────────────────────────────
interface Note {
  id: string
  title: string
  preview: string
  content: string
  updatedAt: string
}

const notes = ref<Note[]>([])
const selectedId = ref<string>('')
const editorRef = ref<HTMLElement>()
let crepe: Crepe | null = null
let saveTimer: ReturnType<typeof setInterval>

const extractTitle = (content: string) => {
  const match = content.match(/^#\s+(.+)/m)
  return match ? match[1].trim() : 'Untitled'
}

const extractPreview = (content: string) => {
  const lines = content
    .split('\n')
    .map(l => l.replace(/<[^>]*>/g, '').trim())
    .filter(l => l && !l.startsWith('#'))
  return lines[0]?.slice(0, 60) || ''
}

const formatDate = (iso: string) => {
  const d = new Date(iso)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// ── Editor ────────────────────────────────────────────────
const initEditor = async (content: string) => {
  if (crepe) { crepe.destroy(); crepe = null }
  if (!editorRef.value) return
  editorRef.value.innerHTML = ''

  crepe = new Crepe({ root: editorRef.value, defaultValue: content })
  await crepe.create()

  clearInterval(saveTimer)
  saveTimer = setInterval(async () => {
    if (!crepe || !selectedId.value) return
    const md = await crepe.getMarkdown()
    const note = notes.value.find(n => n.id === selectedId.value)
    if (note && md !== note.content) {
      note.content = md
      note.title = extractTitle(md)
      note.preview = extractPreview(md)
      note.updatedAt = new Date().toISOString()
    }
  }, 1500)
}

// ── Note actions ───────────────────────────────────────────
const selectNote = (id: string) => { selectedId.value = id }

const createNote = () => {
  const note: Note = {
    id: crypto.randomUUID(),
    title: 'Untitled',
    preview: '',
    content: '# Untitled\n\n',
    updatedAt: new Date().toISOString(),
  }
  notes.value.unshift(note)
  selectedId.value = note.id
}

watch(selectedId, async (id) => {
  if (!id) return
  await nextTick()
  const note = notes.value.find(n => n.id === id)
  if (note) initEditor(note.content)
}, { flush: 'post' })

onBeforeUnmount(() => {
  clearInterval(saveTimer)
  crepe?.destroy()
})
</script>

<style>
/* ── Milkdown / Crepe 主题覆盖 ── */
.milkdown {
  --crepe-color-background: #F4F3EE;
  --crepe-color-on-background: var(--color-base-content);
  --crepe-color-surface: #ece9e3;
  --crepe-color-surface-low: #e2dfd9;
  --crepe-color-on-surface: var(--color-base-content);
  --crepe-color-outline: var(--color-base-content);
  --crepe-color-primary: var(--color-primary);
  --crepe-color-hover: #e2dfd9;
  --crepe-color-selected: #d8d5cf;
  --crepe-font-default: ui-sans-serif, system-ui, sans-serif;
  --crepe-font-title: ui-sans-serif, system-ui, sans-serif;
  height: 100% !important;
  min-height: 100% !important;
  background: #F4F3EE !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* ── Crepe frame 主题默认 padding: 60px 120px，覆盖为合理值 ── */
.milkdown .ProseMirror {
  padding: 48px clamp(20px, 6%, 64px) !important;
}

/* ── 代码块：正文白底，gutter 同步白底 ── */
.milkdown .cm-editor,
.milkdown .cm-scroller {
  background-color: #fff !important;
}
.milkdown .cm-gutters {
  background-color: #fff !important;
  border-right: none !important;
}

/* ── 当前行高亮：去掉行号变黑 ── */
.milkdown .cm-activeLineGutter { background-color: transparent !important; color: inherit !important; }
.milkdown .cm-activeLine { background-color: transparent !important; }

/* ── 隐藏代码块自动补全下拉框（保留括号自动闭合） ── */
.milkdown .cm-tooltip-autocomplete { display: none !important; }

/* ── 图标颜色：milkdown-icon ── */
.milkdown .milkdown-icon svg,
.milkdown .milkdown-icon svg * {
  fill: var(--color-base-content) !important;
  color: var(--color-base-content) !important;
}

/* ── 图标颜色：浮层组件（block-handle / toolbar / slash 等）── */
.milkdown > *:not(.ProseMirror) svg,
.milkdown > *:not(.ProseMirror) svg * {
  fill: var(--color-base-content) !important;
  color: var(--color-base-content) !important;
}

/* ── 列表 label 颜色继承 ── */
.milkdown .milkdown-list-item-block .label-wrapper {
  color: var(--color-base-content) !important;
}

/* ── 代码块头部：始终可见，无背景 ── */
.milkdown .milkdown-code-block .tools .tools-button-group button { opacity: 1 !important; }
.milkdown .milkdown-code-block .tools .language-button {
  opacity: 1 !important;
  background: transparent !important;
  box-shadow: none !important;
}

/* ── Copy 按钮：去掉文字，换 Phosphor PhCopy 图标 ── */
.milkdown .copy-button {
  font-size: 0 !important;
  gap: 0 !important;
  padding: 4px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: transparent !important;
}
.milkdown .copy-button .milkdown-icon { display: none !important; }
.milkdown .copy-button::before {
  content: '';
  display: block;
  width: 14px;
  height: 14px;
  background-color: currentColor;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32Zm-56,176H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z'/%3E%3C/svg%3E") no-repeat center / contain;
  -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath d='M216,32H88a8,8,0,0,0-8,8V80H40a8,8,0,0,0-8,8V216a8,8,0,0,0,8,8H168a8,8,0,0,0,8-8V176h40a8,8,0,0,0,8-8V40A8,8,0,0,0,216,32Zm-56,176H48V96H160Zm48-48H176V88a8,8,0,0,0-8-8H96V48H208Z'/%3E%3C/svg%3E") no-repeat center / contain;
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
</style>
