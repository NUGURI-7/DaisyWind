<template>
  <!-- 
    移动端采用方案B（高级原生抽屉体验）：
    - 大屏 (lg+): 正常的 Flex 平铺布局，Sidebar 挤压 Main 区域。
    - 小屏: Sidebar 变为 fixed 定位，浮在 Main 之上，并配有可点击关闭的半透明黑色遮罩 (Backdrop)。
  -->
  <div class="flex h-[100dvh] relative overflow-hidden bg-background">
    <!-- 移动端遮罩 Backdrop (仅小屏且展开时显示) -->
    <Transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="!isLargeScreen && isDrawerOpen"
        class="fixed inset-0 z-40 bg-black/50 lg:hidden"
        @click="isDrawerOpen = false"
        aria-hidden="true"
      ></div>
    </Transition>

    <!-- Sidebar 区域 
         小屏时 fixed 定位，靠左边缘，利用 transform 实现侧滑
         大屏时 static 定位，占据真实文档流宽度
    -->
    <div
      class="fixed inset-y-0 left-0 z-50 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0"
      :class="[!isLargeScreen && !isDrawerOpen ? '-translate-x-full' : 'translate-x-0']"
    >
      <Sidebar :is-open="isDrawerOpen" @toggle="isDrawerOpen = !isDrawerOpen" />
    </div>

    <!-- Main 区域 -->
    <div class="flex-1 flex flex-col min-w-0 h-full relative z-0">
      <!-- 移动端 toggle 按钮 (仅小屏显示) -->
      <div class="shrink-0 p-3 lg:hidden flex items-center border-b border-border bg-background">
        <button
          @click="isDrawerOpen = !isDrawerOpen"
          class="flex items-center justify-center size-9 rounded-md text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer"
          aria-label="Toggle sidebar"
        >
          <PhSidebarSimple :size="20" />
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 min-h-0">
        <MainContent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useBreakpoints } from '@vueuse/core'
import { PhSidebarSimple } from '@phosphor-icons/vue'

import MainContent from './MainContent.vue'
import Sidebar from './Sidebar.vue'
import { userAuthStore } from '@/stores/auth'

const authStore = userAuthStore()

// 定义断点（Tailwind CSS 默认断点）
const breakpoints = useBreakpoints({
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
})

// 判断是否大屏
const isLargeScreen = breakpoints.greaterOrEqual('lg')

// 从 localStorage 读取上次状态，默认展开
const _saved = localStorage.getItem('sidebar-open')
const userDrawerState = ref(_saved !== null ? _saved === 'true' : true)
const isDrawerOpen = ref(userDrawerState.value)

// 监听屏幕变化
watch(
  isLargeScreen,
  (isLarge) => {
    if (!isLarge) {
      // 切换到小屏时自动隐藏 Sidebar
      isDrawerOpen.value = false
    } else {
      // 切换到大屏时恢复用户偏好或默认展开
      isDrawerOpen.value = userDrawerState.value
    }
  },
  { immediate: true },
)

// 监听用户操作，保存偏好到内存和 localStorage
watch(isDrawerOpen, (value) => {
  if (isLargeScreen.value) {
    userDrawerState.value = value
    localStorage.setItem('sidebar-open', String(value))
  }
})

onMounted(() => {
  authStore.fetchCurrentUser()
  // 后台预加载 Notes chunk（含 Milkdown），消除首次点击延迟
  import('@/views/notes/index.vue')
})
</script>
