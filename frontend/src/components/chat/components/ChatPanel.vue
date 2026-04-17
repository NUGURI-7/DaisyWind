<template>
  <div class="flex flex-col h-full min-h-0 bg-background">
    <MessageList />
    <MessageInput />
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import { useChatStore } from '@/stores/chat'

defineOptions({ name: 'ChatPanel' })

const route = useRoute()
const chat = useChatStore()

// URL ↔ 对话 同步：URL 是单一真相源
watch(
  () => route.params.uuid,
  (uuid) => {
    if (typeof uuid === 'string' && uuid) {
      chat.loadConversation(uuid)
    } else {
      chat.newConversation()
    }
  },
  { immediate: true },
)
</script>
