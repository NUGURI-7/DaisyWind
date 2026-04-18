<template>
  <div class="text-block">
    <p class="whitespace-pre-wrap wrap-break-word leading-relaxed">{{ block.content }}</p>
    <ThreeSpinner
      v-if="block.status === 'active' || keepSpinner"
      :size="36"
      :active="block.status === 'active'"
      class="mt-2"
    />
  </div>
</template>

<script setup lang="ts">
import ThreeSpinner from '@/components/common/ThreeSpinner.vue'
import type { TextBlock } from '@/types/chat'

defineProps<{
  block: TextBlock
  keepSpinner?: boolean
}>()
</script>
