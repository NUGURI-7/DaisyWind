<template>
  <div
    class="flex min-h-full flex-col items-start bg-base-300 is-drawer-close:w-14 is-drawer-open:w-64"
  >
    <div
      class="w-full flex items-center justify-between p-2 is-drawer-close:flex-col is-drawer-close:items-center is-drawer-close:gap-2"
    >
      <img src="/raccoon-pa.svg" class="w-16" alt="daisyUI logo" />
      <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
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

    <ul class="menu w-full grow">
      <li>
        <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Homepage">
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
            <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path>
            <path
              d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
            ></path>
          </svg>
          <span class="is-drawer-close:hidden">Homepage</span>
        </button>
      </li>

      <li>
        <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Settings">
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
            <path d="M20 7h-9"></path>
            <path d="M14 17H5"></path>
            <circle cx="17" cy="17" r="3"></circle>
            <circle cx="7" cy="7" r="3"></circle>
          </svg>
          <span class="is-drawer-close:hidden">Settings</span>
        </button>
      </li>
    </ul>
    <!-- 主题切换器 - 展开时显示 -->
    <div class="w-full p-2 is-drawer-close:hidden">
      <select v-model="theme" class="select select-bordered w-full select-sm">
        <option disabled>选择主题</option>
        <option v-for="t in themes" :key="t" :value="t">
          {{ t }}
        </option>
      </select>
    </div>

    <!-- 主题切换器 - 收起时显示 -->
    <div class="is-drawer-open:hidden p-2 w-full">
      <div class="dropdown dropdown-right w-full">
        <label
          tabindex="0"
          class="btn btn-square btn-ghost btn-sm w-full tooltip tooltip-right"
          data-tip="主题"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            class="size-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
            />
          </svg>
        </label>
        <ul
          tabindex="0"
          class="dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 max-h-96 overflow-y-auto z-50"
        >
          <li v-for="t in themes" :key="t">
            <a @click="setTheme(t)" :class="{ active: theme === t }">{{ t }}</a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { userTheme } from '@/composables/useTheme'

const { theme, setTheme, themes } = userTheme()
</script>
