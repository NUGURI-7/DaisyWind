<template>
  <div class="flex-1 min-h-0 flex flex-col w-full">
    <!-- 顶部标题与新建按钮 -->
    <div class="flex items-center justify-between px-2 pt-4 pb-1 shrink-0">
      <h3 class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Notes</h3>
      <button
        @click="createNote"
        class="flex items-center justify-center size-6 rounded hover:bg-sidebar-accent hover:text-sidebar-accent-foreground text-muted-foreground transition-colors"
        aria-label="New Note"
      >
        <PhPlus :size="14" />
      </button>
    </div>

    <!-- 滚动列表 -->
    <div class="flex-1 min-h-0 overflow-y-auto">
      <p
        v-if="store.orderedIds.length === 0"
        class="text-muted-foreground text-xs text-center px-2 py-4"
      >
        暂无笔记
      </p>

      <ul class="space-y-0.5">
        <li
          v-for="id in store.orderedIds"
          :key="id"
          :class="[
            'group relative flex items-center gap-2 rounded-md px-2 py-1.5 cursor-pointer transition',
            id === store.selectedId
              ? 'bg-sidebar-accent text-sidebar-accent-foreground'
              : 'text-sidebar-foreground hover:bg-sidebar-accent',
          ]"
          @click="selectNote(id)"
        >
          <!-- 标题区，超出截断 -->
          <span class="flex-1 truncate text-sm">
            {{ store.notesById[id]?.title || 'Untitled' }}
          </span>

          <!-- 右侧时间 (hover 时隐藏，为删除按钮让位) -->
          <span class="text-[10px] text-muted-foreground/70 shrink-0 group-hover:hidden">
            {{ formatDateShort(store.notesById[id]?.updated_at) }}
          </span>

          <!-- 删除按钮 (hover 时出现) -->
          <button
            class="hidden group-hover:flex shrink-0 size-5 items-center justify-center rounded hover:bg-destructive/10 hover:text-destructive transition"
            @click.stop="confirmDelete(id)"
            aria-label="删除笔记"
          >
            <PhTrash :size="14" />
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNoteStore } from '@/stores/notes'
import { useRouter } from 'vue-router'
import { PhPlus, PhTrash } from '@phosphor-icons/vue'

const store = useNoteStore()
const router = useRouter()

// 短日期格式化：今天显示 HH:mm，之前显示 MM-DD
const formatDateShort = (iso?: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  const today = new Date()
  if (
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()
  ) {
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return d.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
}

const selectNote = async (uuid: string) => {
  if (uuid === store.selectedId) return
  await store.flush()
  store.selectedId = uuid
  router.push({ query: { id: uuid } })
}

const createNote = async () => {
  const newId = await store.create()
  if (newId) {
    router.push({ query: { id: newId } })
  }
}

// 这里的删除我们借用一下浏览器原生的 confirm，或者你可以按原样在外部处理
// 为了简化侧边栏，这里用最简单的 confirm
const confirmDelete = async (id: string) => {
  if (confirm('确定要删除这条笔记吗？此操作无法撤销。')) {
    await store.remove(id)
    if (store.selectedId === id) {
      store.selectedId = null
      router.push({ query: {} })
    }
  }
}
</script>
