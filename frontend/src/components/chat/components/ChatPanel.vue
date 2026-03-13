<template>
  <div class="flex h-full flex-col p-4 max-w-4xl mx-auto w-full">
    <!-- Chat Messages Area -->
    <div class="flex-1 overflow-y-auto flex flex-col gap-6 py-4">
      <!-- AI Message (Left) -->
      <div class="flex justify-start w-full">
        <div class="bg-muted text-foreground rounded-2xl rounded-tl-sm px-4 py-2.5 max-w-[75%] text-sm shadow-sm">
          Hello
        </div>
      </div>
      
      <!-- User Message (Right) -->
      <div class="flex justify-end w-full">
        <div class="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-[75%] text-sm shadow-sm">
          Hi
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="shrink-0 mt-auto pt-4 border-t border-border flex gap-3">
      <Input class="w-full flex-1" placeholder="Type a message..." />
      <Button class="shrink-0">Send</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

defineOptions({ name: 'ChatPanel' })
</script>
