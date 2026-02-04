<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" v-model="isDrawerOpen" />
    <!--主区域-->
    <div class="drawer-content">
      <div class="p-2 lg:hidden">
        <label for="my-drawer-4" class="btn btn-square btn-ghost" aria-label="open sidebar">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
            class="my-1.5 inline-block size-4"
          >
            <path
              d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"
            ></path>
            <path d="M9 4v16"></path>
            <path d="M14 10l2 2l-2 2"></path>
          </svg>
        </label>
      </div>
      <MainContent></MainContent>
    </div>
    <!--侧边栏-->
    <div class="drawer-side">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <Sidebar></Sidebar>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue'
import MainContent from './MainContent.vue'
import Sidebar from './Sidebar.vue'
import { useBreakpoints } from '@vueuse/core'

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
// 用户手动控制的状态
const userDrawerState = ref(true)
// 计算属性：大屏时始终展开，小屏时由用户控制
const isDrawerOpen = ref(true)

// 监听屏幕变化
watch(
  isLargeScreen,
  (isLarge) => {
    if (!isLarge) {
      // 切换到小屏时自动关闭
      isDrawerOpen.value = false
    } else {
      // 切换到大屏时恢复用户偏好或默认展开
      isDrawerOpen.value = userDrawerState.value
    }
  },
  { immediate: true },
)

// 监听用户操作，保存偏好
watch(isDrawerOpen, (value) => {
  if (isLargeScreen.value) {
    userDrawerState.value = value
  }
})
</script>
