<template>
  <ul class="list bg-base-100 rounded-box shadow-md">
    <li class="p-4 pb-2 text-xs opacity-60 tracking-wide">Most played songs this week</li>

    <li class="list-row">
      <div>
        <img
          class="size-10 rounded-box"
          src="https://img.daisyui.com/images/profile/demo/1@94.webp"
        />
      </div>
      <div>
        <div>Dio Lupa</div>
        <div class="text-xs uppercase font-semibold opacity-60">Remaining Reason</div>
      </div>
      <p class="list-col-wrap text-xs">
        "Remaining Reason" became an instant hit, praised for its haunting sound and emotional
        depth. A viral performance brought it widespread recognition, making it one of Dio Lupa’s
        most iconic tracks.
      </p>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path d="M6 3L20 12 6 21 6 3z"></path>
          </g>
        </svg>
      </button>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path
              d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
            ></path>
          </g>
        </svg>
      </button>
    </li>

    <li class="list-row">
      <div>
        <img
          class="size-10 rounded-box"
          src="https://img.daisyui.com/images/profile/demo/4@94.webp"
        />
      </div>
      <div>
        <div>Ellie Beilish</div>
        <div class="text-xs uppercase font-semibold opacity-60">Bears of a fever</div>
      </div>
      <p class="list-col-wrap text-xs">
        "Bears of a Fever" captivated audiences with its intense energy and mysterious lyrics. Its
        popularity skyrocketed after fans shared it widely online, earning Ellie critical acclaim.
      </p>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path d="M6 3L20 12 6 21 6 3z"></path>
          </g>
        </svg>
      </button>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path
              d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
            ></path>
          </g>
        </svg>
      </button>
    </li>

    <li class="list-row">
      <div>
        <img
          class="size-10 rounded-box"
          src="https://img.daisyui.com/images/profile/demo/3@94.webp"
        />
      </div>
      <div>
        <div>Sabrino Gardener</div>
        <div class="text-xs uppercase font-semibold opacity-60">Cappuccino</div>
      </div>
      <p class="list-col-wrap text-xs">
        "Cappuccino" quickly gained attention for its smooth melody and relatable themes. The song’s
        success propelled Sabrino into the spotlight, solidifying their status as a rising star.
      </p>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path d="M6 3L20 12 6 21 6 3z"></path>
          </g>
        </svg>
      </button>
      <button class="btn btn-square btn-ghost">
        <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
          <g
            stroke-linejoin="round"
            stroke-linecap="round"
            stroke-width="2"
            fill="none"
            stroke="currentColor"
          >
            <path
              d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
            ></path>
          </g>
        </svg>
      </button>
    </li>
  </ul>
  <div class="my-1 flex w-full justify-center gap-1">
    <kbd
      v-for="key in row1"
      :key="key"
      class="kbd cursor-pointer select-none transition-all duration-100"
      :class="
        pressedKey === key
          ? 'scale-90 brightness-75 shadow-none'
          : 'hover:brightness-90 active:scale-95'
      "
      @mousedown="handleKeyDown(key)"
      @mouseup="handleKeyUp"
      @mouseleave="handleKeyUp"
    >
      {{ key }}
    </kbd>
  </div>
  <div class="my-1 flex w-full justify-center gap-1">
    <kbd
      v-for="key in row2"
      :key="key"
      class="kbd cursor-pointer select-none transition-all duration-100"
      :class="
        pressedKey === key
          ? 'scale-90 brightness-75 shadow-none'
          : 'hover:brightness-90 active:scale-95'
      "
      @mousedown="handleKeyDown(key)"
      @mouseup="handleKeyUp"
      @mouseleave="handleKeyUp"
    >
      {{ key }}
    </kbd>
  </div>
  <div class="my-1 flex w-full justify-center gap-1">
    <kbd
      v-for="key in row3"
      :key="key"
      class="kbd cursor-pointer select-none transition-all duration-100"
      :class="
        pressedKey === key
          ? 'scale-90 brightness-75 shadow-none'
          : 'hover:brightness-90 active:scale-95'
      "
      @mousedown="handleKeyDown(key)"
      @mouseup="handleKeyUp"
      @mouseleave="handleKeyUp"
    >
      {{ key }}
    </kbd>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const row1 = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
const row2 = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
const row3 = ['z', 'x', 'c', 'v', 'b', 'n', 'm', '/']

const allKeys = [...row1, ...row2, ...row3]

const pressedKey = ref<string | null>(null)

const emit = defineEmits<{
  keyPress: [key: string]
}>()

// 鼠标点击
function handleKeyDown(key: string) {
  pressedKey.value = key
  emit('keyPress', key)
}

function handleKeyUp() {
  pressedKey.value = null
}

// 物理键盘
function onKeyboardDown(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  if (allKeys.includes(key) && pressedKey.value !== key) {
    pressedKey.value = key
    emit('keyPress', key)
  }
}

function onKeyboardUp(event: KeyboardEvent) {
  const key = event.key.toLowerCase()
  if (pressedKey.value === key) {
    pressedKey.value = null
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeyboardDown)
  window.addEventListener('keyup', onKeyboardUp)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyboardDown)
  window.removeEventListener('keyup', onKeyboardUp)
})
</script>

<style scoped></style>
