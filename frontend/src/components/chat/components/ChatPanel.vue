<template>
  <div class="flex h-full flex-col gap-4 p-4">
    <div class="chat chat-start">
      <div class="chat-bubble">Hello</div>
    </div>
    <div class="chat chat-end">
      <div class="chat-bubble chat-bubble-primary">Hi</div>
    </div>

    <div class="mt-auto flex gap-2">
      <input class="input input-bordered w-full" placeholder="Type a message..." />
      <button class="btn btn-primary">Send</button>
    </div>
  </div>
</template>
<script setup lang="ts">
defineOptions({ name: 'ChatPanel' })
</script>
