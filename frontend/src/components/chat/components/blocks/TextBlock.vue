<template>
  <div class="text-block">
    <p class="whitespace-pre-wrap wrap-break-word leading-relaxed">{{ block.content }}</p>
  </div>
</template>

<script setup lang="ts">
import type { TextBlock } from '@/types/chat'

defineProps<{
  block: TextBlock
}>()
</script>
