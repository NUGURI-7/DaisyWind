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
          <template v-for="block in msg.blocks" :key="block.index">
            <TextBlock
              v-if="block.type === 'text'"
              :block="block"
              :keep-spinner="msg.uuid === chat.lastAssistantUuid && isLastTextBlock(msg, block)"
            />
            <ToolUseBlock v-else-if="block.type === 'tool_use'" :block="block" />
          </template>
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
import ToolUseBlock from './blocks/ToolUseBlock.vue'
import type { ChatMessage, RenderBlock } from '@/types/chat'

const chat = useChatStore()

// 判断 block 是否是 msg 里最后一个 text block
function isLastTextBlock(msg: ChatMessage, block: RenderBlock) {
  // 1. 类型守卫：如果是 user 消息（或者没有 blocks），直接返回 false
  if (msg.role === 'user' || !('blocks' in msg)) {
    return false
  }

  // 2. 此时 TypeScript 已经自动推断 msg 是 AssistantMessage
  // 下面就不需要写 msg.blocks! 了，直接写 msg.blocks 即可
  for (let i = msg.blocks.length - 1; i >= 0; i--) {
    if (msg.blocks[i]!.type === 'text') {
      return msg.blocks[i]!.index === block.index
    }
  }

  return false
}
</script>
