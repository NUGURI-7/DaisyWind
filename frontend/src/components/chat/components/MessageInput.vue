<template>
  <div class="shrink-0 px-4 py-4 pb-8">
    <div class="max-w-3xl mx-auto">
      <div
        class="relative flex items-end gap-2 rounded-2xl border border-border bg-background px-4 py-3 focus-within:border-ring"
      >
        <textarea
          v-model="input"
          :disabled="chat.isLoading"
          rows="1"
          placeholder="发送消息..."
          class="flex-1 resize-none bg-transparent outline-none placeholder:text-muted-foreground disabled:opacity-50 max-h-40"
          @keydown.enter.exact.prevent="handleSend"
          @input="autoResize"
          ref="textareaRef"
        ></textarea>
        <button
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
import { useChatStore } from '@/stores/chat'

const chat = useChatStore()
const input = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

async function handleSend() {
  const content = input.value.trim()
  if (!content || chat.isLoading) return

  input.value = ''
  await nextTick()
  autoResize()

  await chat.sendMessage({
    message_uuid: crypto.randomUUID(),
    content,
    provider: 'deepseek',
    model: 'deepseek-chat',
  })
}
</script>
