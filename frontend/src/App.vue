<script setup lang="ts">
import { Toaster } from 'vue-sonner'
</script>

<template>
  <div>
    <Toaster position="top-center" richColors />
    <RouterView />
  </div>
</template>
