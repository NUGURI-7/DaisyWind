<template>
  <div class="h-full">
    <ChatPanel></ChatPanel>
  </div>
</template>
<script setup lang="ts">
import ChatPanel from './components/ChatPanel.vue'

defineOptions({ name: 'Chat' })
</script>
