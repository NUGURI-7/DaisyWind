<script setup lang="ts">
import { Toaster } from 'vue-sonner'
import 'vue-sonner/style.css'
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
