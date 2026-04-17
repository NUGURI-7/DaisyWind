<template>
  <div class="flex-1 min-h-0 overflow-y-auto px-4 py-6">
    <div class="max-w-3xl mx-auto space-y-6">
      <div v-for="msg in chat.messages" :key="msg.uuid">
        <!-- User 消息 -->
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="max-w-[80%] rounded-2xl bg-muted text-foreground px-4 py-2.5">
            <p class="whitespace-pre-wrap wrap-break-word">{{ msg.content }}</p>
          </div>
        </div>

        <!-- Assistant 消息 -->
        <div v-else class="flex flex-col gap-2">
          <TextBlock v-for="block in msg.blocks" :key="block.index" :block="block" />
          <p v-if="msg.status === 'error'" class="text-destructive text-sm">
            {{ msg.errorMessage }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'
import TextBlock from './blocks/TextBlock.vue'

const chat = useChatStore()
</script>
