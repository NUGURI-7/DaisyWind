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
    <!-- 底部用户信息 -->
    <!-- 底部用户信息 -->
    <div class="w-full p-2">
      <details class="dropdown mb-2 dropdown-top w-full">
        <summary
          class="btn btn-ghost w-full justify-start h-14 is-drawer-close:btn-square is-drawer-close:justify-center"
        >
          <div class="flex items-center gap-3">
            <img src="/fcb.svg" class="size-8" alt="avatar" />
            <div class="is-drawer-close:hidden flex items-center gap-2">
              <span class="text-sm text-base-content/75 leading-none">{{
                authStore.user?.nick_name
              }}</span>
              <span
                v-if="authStore.user?.rank_title"
                class="text-xs font-semibold bg-yellow-700/20 text-yellow-800 px-1.5 py-0.5 rounded inline-flex items-center leading-none"
              >
                {{ authStore.user?.rank_title }}
              </span>
            </div>
          </div>
        </summary>
        <ul class="dropdown-content menu rounded-box bg-base-100 shadow-lg w-full p-2 mb-2 z-50">
          <li class="menu-title">{{ authStore.user?.email }}</li>
          <li><button disabled>Settings</button></li>
          <li><button disabled>Language</button></li>
          <div class="divider my-0"></div>
          <li>
            <button @click="handleLogout" class="font-bold">Log out</button>
          </li>
        </ul>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { userAuthStore } from '@/stores/auth'

const authStore = userAuthStore()

function handleLogout() {
  setTimeout(() => authStore.logout(), 500)
}
</script>
