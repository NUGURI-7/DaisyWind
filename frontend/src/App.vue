<script setup lang="ts">
import { provide } from 'vue'
import { Toaster } from 'vue-sonner'
import 'vue-sonner/style.css'
import { useTheme } from '@/composables/useTheme'

provide('weight', 'bold')

// 启动时立即应用保存的主题（防止白屏闪烁）
const { applyTheme } = useTheme()
applyTheme()
</script>

<template>
  <div>
    <Toaster
      :closeButton="true"
      closeButtonPosition="bottom-right"
      position="top-center"
      richColors
      :toastOptions="{
        class: 'rounded-xl text-sm shadow-lg',
      }"
    />
    <RouterView />
  </div>
</template>
