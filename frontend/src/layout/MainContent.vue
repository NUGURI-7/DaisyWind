<template>
  <div class="h-full flex flex-col bg-background">
    <!-- Navbar -->
    <div class="relative shrink-0 z-10 border-b border-border/40">
      <header
        class="h-14 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center px-4 relative"
      >
        <!-- 侧边栏切换按钮（仅小屏幕显示，lg 断点以上隐藏） -->
        <button
          @click="$emit('toggle-sidebar')"
          class="lg:hidden flex items-center justify-center size-9 -ml-1 mr-2 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors z-10 cursor-pointer"
          aria-label="Toggle sidebar"
        >
          <PhSidebarSimple :size="20" />
        </button>

        <!-- 页面标题（小屏绝对居中，大屏靠左流动） -->
        <div
          class="absolute inset-0 flex items-center justify-center pointer-events-none lg:static lg:inset-auto lg:flex-1 lg:justify-start lg:pl-2"
        >
          <span
            class="text-sm font-semibold text-foreground tracking-tight pointer-events-auto truncate px-12 lg:px-0"
          >
            {{ pageTitle }}
          </span>
        </div>
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
import { PhSidebarSimple } from '@phosphor-icons/vue'

const route = useRoute()

// 定义向父组件派发的事件
defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/chat': 'Chat',
    '/notes': 'Notes',
  }
  return titles[route.path] ?? ''
})
</script>
