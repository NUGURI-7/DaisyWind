<template>
  <div class="h-screen flex flex-col">
    <!-- Navbar -->
    <div class="relative shrink-0 z-10">
      <header class="h-12 bg-base-100 flex items-center px-4">
        <span class="text-sm font-medium text-base-content/50">{{ pageTitle }}</span>
      </header>
      <!-- 底部渐变淡出遮罩 -->
      <div class="absolute inset-x-0 top-full h-8 pointer-events-none bg-gradient-to-b from-base-100 to-transparent"></div>
    </div>
    <!-- 可滚动内容区 -->
    <div class="flex-1 overflow-y-auto">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/chat': 'Chat',
    '/notes': 'Notes',
  }
  return titles[route.path] ?? ''
})
</script>
