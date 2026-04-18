<template>
  <div class="h-full flex flex-col bg-background">
    <!-- Navbar -->
    <div class="relative shrink-0 z-10 border-b border-border/40">
      <header
        class="h-14 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center px-6"
      >
        <span class="text-sm font-semibold text-foreground tracking-tight">{{ pageTitle }}</span>
      </header>
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
