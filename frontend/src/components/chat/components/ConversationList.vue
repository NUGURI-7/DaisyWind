<template>
  <div class="flex flex-col min-h-0 flex-1 px-2">
    <!-- Section label -->
    <h3
      class="shrink-0 px-2 pt-4 pb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider"
    >
      Recents
    </h3>

    <!-- 滚动列表 -->
    <div class="flex-1 min-h-0 overflow-y-auto">
      <p
        v-if="chat.conversations.length === 0"
        class="text-muted-foreground text-xs text-center px-2 py-4"
      >
        暂无对话
      </p>

      <ul class="space-y-0.5">
        <li
          v-for="conv in chat.conversations"
          :key="conv.uuid"
          :class="[
            'group relative flex items-center gap-2 rounded-md px-2 py-1.5 cursor-pointer transition',
            conv.uuid === chat.currentConversationUuid
              ? 'bg-sidebar-accent text-sidebar-accent-foreground'
              : 'text-sidebar-foreground hover:bg-sidebar-accent',
          ]"
          @click="handleSelect(conv.uuid)"
        >
          <span class="flex-1 truncate text-sm">{{ conv.title || '未命名' }}</span>

          <button
            class="opacity-0 group-hover:opacity-100 shrink-0 p-1 rounded hover:bg-destructive/10 hover:text-destructive transition"
            @click.stop="handleDelete(conv)"
            aria-label="删除对话"
          >
            <PhTrash :size="12" />
          </button>
        </li>
      </ul>
    </div>
    <AlertDialog :open="showDeleteDialog" @update:open="showDeleteDialog = $event">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete chat</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to delete this chat?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="showDeleteDialog = false">Cancel</AlertDialogCancel>
          <!-- 使用 destructive 颜色来匹配红色的删除按钮 -->
          <AlertDialogAction
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            @click="executeDelete"
          >
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { PhTrash } from '@phosphor-icons/vue'
import { useChatStore } from '@/stores/chat'
import type { ConversationSummary } from '@/api/chat'

// --- 添加 AlertDialog 相关的导入 ---
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

defineOptions({ name: 'ConversationList' })

const chat = useChatStore()
const router = useRouter()

const showDeleteDialog = ref(false)
const itemToDelete = ref<ConversationSummary | null>(null)

onMounted(() => {
  chat.loadConversations()
})

function handleSelect(uuid: string) {
  router.push(`/chat/${uuid}`)
}

function handleDelete(conv: ConversationSummary) {
  itemToDelete.value = conv
  showDeleteDialog.value = true
}

async function executeDelete() {
  if (!itemToDelete.value) return

  const conv = itemToDelete.value
  const wasCurrent = chat.currentConversationUuid === conv.uuid
  await chat.removeConversation(conv.uuid)

  if (wasCurrent) {
    router.push('/chat')
  }

  // 清理状态
  showDeleteDialog.value = false
  itemToDelete.value = null
}
</script>
