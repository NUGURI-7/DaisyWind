<template>
  <div class="shrink-0 px-4 py-4 pb-8">
    <div class="max-w-3xl mx-auto">
      <div
        class="relative flex items-end gap-2 rounded-2xl border border-border bg-background px-4 py-3 focus-within:border-ring"
      >
        <textarea
          v-model="input"
          rows="1"
          placeholder="发送消息..."
          class="flex-1 resize-none bg-transparent outline-none placeholder:text-muted-foreground max-h-40"
          @compositionstart="isComposing = true"
          @compositionend="isComposing = false"
          @keydown.enter.exact="handleEnter"
          @input="autoResize"
          ref="textareaRef"
        ></textarea>
        <!-- 恢复了 disabled，去掉了多余的 touch 事件，保持 type="button" -->
        <button
          type="button"
          :disabled="chat.isLoading || !input.trim()"
          class="shrink-0 rounded-lg p-2 bg-primary text-primary-foreground disabled:opacity-40 disabled:cursor-not-allowed hover:bg-primary/90 transition"
          @click="handleSend"
        >
          <PhPaperPlaneTilt :size="18" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { PhPaperPlaneTilt } from '@phosphor-icons/vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { v4 as uuidv4 } from 'uuid' // 使用刚刚讨论的稳定的 uuid 库

const chat = useChatStore()
const route = useRoute()
const router = useRouter()

const input = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// 生产级输入法处理与防抖
const isComposing = ref(false)
const isSending = ref(false)

const handleEnter = (e: KeyboardEvent) => {
  if (isComposing.value) return
  e.preventDefault()
  handleSend()
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

async function handleSend() {
  // 回归纯净的 Vue 取值
  const contentToSend = input.value.trim()

  // 恢复所有的严格拦截
  if (!contentToSend || chat.isLoading || isSending.value) {
    return
  }

  try {
    isSending.value = true

    // 清空 UI 给反馈
    input.value = ''
    await nextTick()
    autoResize()
    textareaRef.value?.focus()

    if (!route.params.uuid && chat.currentConversationUuid) {
      router.push(`/chat/${chat.currentConversationUuid}`)
    }

    // 调用网络请求（使用安全的 uuidv4）
    await chat.sendMessage({
      message_uuid: uuidv4(),
      content: contentToSend,
      provider: 'deepseek',
      model: 'deepseek-chat',
    })
  } finally {
    isSending.value = false
  }
}
</script>
