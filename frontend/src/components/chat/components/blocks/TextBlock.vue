<template>
  <div class="text-block">
    <p class="whitespace-pre-wrap wrap-break-word leading-relaxed">{{ block.content }}</p>
    <span v-if="block.status === 'active'" class="streaming-cursor" aria-hidden="true"></span>
  </div>
</template>

<script setup lang="ts">
import type { TextBlock } from '@/types/chat'

defineProps<{
  block: TextBlock
}>()
</script>

<style scoped>
@keyframes cursor-blink {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

.streaming-cursor::after {
  content: '▊';
  margin-left: 2px;
  animation: cursor-blink 1s step-end infinite;
  opacity: 0.7;
}
</style>
