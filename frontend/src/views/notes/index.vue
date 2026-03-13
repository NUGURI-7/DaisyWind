<template>
  <div class="flex h-full">
    <!-- 左侧笔记列表 -->
    <div
      class="shrink-0 overflow-hidden transition-[width] duration-300"
      :class="listVisible ? 'w-52' : 'w-0'"
    >
      <div class="w-52 h-full flex flex-col border-r border-border">
        <div class="p-2 border-b border-border">
          <div class="new-note-wrap">
            <button
              @click="createNote"
              class="flex items-center w-full h-8 px-3 gap-2 rounded-md text-sm font-medium border border-dashed border-border text-muted-foreground hover:text-foreground hover:bg-muted hover:border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 cursor-pointer"
            >
              <PhPlus :size="14" />
              New Note
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto">
          <button
            v-for="id in store.orderedIds"
            :key="id"
            @click="selectNote(id)"
            class="group relative w-full text-left p-3 transition-all duration-200 cursor-pointer border-b border-border/50 hover:bg-muted/50 focus-visible:outline-none focus-visible:bg-muted"
            :class="[id === store.selectedId ? 'bg-muted/80 pr-2 pl-4' : 'hover:pl-4']"
          >
            <!-- 选中状态左侧指示线 -->
            <div
              class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] rounded-r-full bg-primary transition-all duration-300"
              :class="id === store.selectedId ? 'h-3/5 opacity-100' : 'h-0 opacity-0'"
            ></div>

            <div class="flex items-center justify-between gap-2 mb-1">
              <div
                class="text-sm truncate transition-colors"
                :class="id === store.selectedId ? 'font-semibold text-foreground' : 'font-medium group-hover:text-primary'"
              >
                {{ store.notesById[id]?.title || 'Untitled' }}
              </div>
              <div class="text-[10px] text-muted-foreground/70 shrink-0">
                {{ formatDate(store.notesById[id]?.updated_at) }}
              </div>
            </div>
            <div class="text-xs text-muted-foreground truncate">
              {{ stripHtml(store.notesById[id]?.preview) || 'No content' }}
            </div>
          </button>

          <div
            v-if="store.orderedIds.length === 0"
            class="px-3 py-6 text-xs text-muted-foreground/70 text-center"
          >
            No notes yet
          </div>
        </div>
      </div>
    </div>

    <!-- 分隔条：hover 显示折叠把手 -->
    <div class="w-3 shrink-0 relative group/divider flex items-center justify-center">
      <div class="absolute inset-y-0 left-1/2 w-px bg-border -translate-x-1/2" />
      <button
        @click="listVisible = !listVisible"
        class="relative z-10 flex items-center justify-center w-4 h-7 rounded-full bg-background border border-border shadow-sm opacity-0 group-hover/divider:opacity-100 transition-opacity duration-200 hover:bg-muted cursor-pointer"
      >
        <PhCaretLeft v-if="listVisible" :size="10" />
        <PhCaretRight v-else :size="10" />
      </button>
    </div>

    <!-- 右侧区域 -->
    <div class="flex-1 flex min-w-0 @container overflow-hidden">
      <!-- 编辑列（含 toolbar） -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <!-- Toolbar -->
        <div
          v-if="store.selectedId"
          class="h-10 shrink-0 flex items-center px-4 gap-2 border-b border-border"
        >
          <span class="text-sm font-semibold text-foreground truncate flex-1">
            {{ store.notesById[store.selectedId]?.title || 'Untitled' }}
          </span>

          <!-- 状态指示器区 -->
          <div class="flex items-center gap-1.5 text-xs font-medium shrink-0 h-full">
            <!-- 保存中 (蓝色转圈) -->
            <transition name="fade">
              <span v-if="store.saving === 'saving'" class="flex items-center gap-1.5 text-info">
                <PhSpinner :size="14" class="animate-spin" />
                Saving...
              </span>
            </transition>

            <!-- 保存成功 (绿色对勾，加了 Tailwind 动画让他淡出) -->
            <transition name="fade">
              <span
                v-if="store.saving === 'saved'"
                class="flex items-center gap-1.5 text-success animate-[fadeOut_2s_ease-out_forwards]"
              >
                <PhCheckCircle :size="14" />
                Saved
              </span>
            </transition>

            <!-- 保存失败 (红色警告) -->
            <transition name="fade">
              <span v-if="store.saving === 'error'" class="flex items-center gap-1.5 text-destructive">
                Save failed
              </span>
            </transition>
          </div>

          <button
            @click="confirmDelete"
            class="flex items-center justify-center size-7 rounded-md text-destructive/60 hover:text-destructive hover:bg-destructive/10 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-error/50 shrink-0 cursor-pointer"
            aria-label="Delete note"
          >
            <PhTrash :size="20" />
          </button>
          <button
            @click="aiVisible = !aiVisible"
            class="flex items-center justify-center size-7 rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 shrink-0 cursor-pointer"
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

        <!-- 编辑区域 -->
        <div class="flex-1 overflow-y-auto py-8 pl-8 pr-8 min-w-0 flex flex-col">
          <div v-if="store.selectedId" class="flex-1">
            <div ref="editorRef" class="h-full" />
          </div>
          <div v-else class="flex flex-col items-center justify-center h-full text-center px-4">
            <div
              class="flex items-center justify-center size-16 rounded-full bg-muted/50 text-foreground/20 mb-4"
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

      <!-- AI 面板 -->
      <div
        class="shrink-0 overflow-hidden transition-[width] duration-300"
        :class="aiVisible ? 'w-100' : 'w-0'"
      >
        <div class="w-100 h-full border-l border-border"></div>
      </div>
    </div>

        <!-- 删除确认 modal -->
    <AlertDialog v-model:open="showDeleteDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete note?</AlertDialogTitle>
          <AlertDialogDescription>This action cannot be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction variant="destructive" @click="doDelete">Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount, watch, nextTick, onMounted } from 'vue'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Crepe } from '@milkdown/crepe'
import '@milkdown/crepe/theme/common/style.css'
import '@milkdown/crepe/theme/frame.css'
import {
  PhPlus,
  PhTrash,
  PhCaretLeft,
  PhCaretRight,
  PhLayout,
  PhNoteBlank,
  PhSpinner,
  PhCheckCircle,
} from '@phosphor-icons/vue'
import { useNoteStore } from '@/stores/notes'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const store = useNoteStore()
const listVisible = ref(true)
const aiVisible = ref(false)

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
  return html.replace(/<[^>]*>/g, '').trim()
}

// ── 代码块交互（不变）─────────────────────────────────────
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
  if (crepe) {
    crepe.destroy()
    crepe = null
  }
}

const initEditor = async (content: string) => {
  destroyEditor()
  if (!editorRef.value) return
  editorRef.value.innerHTML = ''

  crepe = new Crepe({ root: editorRef.value, defaultValue: content })
  await crepe.create()
  editorRef.value.querySelector<HTMLElement>('.ProseMirror')?.setAttribute('spellcheck', 'false')
  editorRef.value.addEventListener('click', handleEditorClick)

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

const confirmDelete = () => showDeleteDialog.value = true

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

/* ── 折叠状态：隐藏代码内容 ── */
.milkdown .milkdown-code-block[data-collapsed='1'] .codemirror-host {
  display: none !important;
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
