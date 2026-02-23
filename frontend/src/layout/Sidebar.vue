<template>
  <!--
    Bug fix 说明：
    1. overflow-hidden → overflow-x-clip
       overflow-x-clip 只裁剪水平溢出（折叠动画需要），垂直方向不受影响
       这样 dropdown 可以向上弹出不被裁剪
       （注意：overflow-x: clip 和 overflow-x: hidden 的关键区别是
        clip 可以独立控制单轴，hidden 会把另一轴也变成 auto/scroll）
    2. 底部容器 is-drawer-close:p-0
       折叠时去掉 padding，让 btn-square 正好填满 56px 宽度
       之前 p-2（8px×2）让按钮从 8px 开始，56px 的按钮会溢出被裁掉 8px
    3. dropdown 用 <Teleport to="body"> 完全脱离 sidebar 的 overflow 上下文
       不再受任何祖先容器的 overflow 影响
  -->
  <div
    class="flex min-h-full flex-col items-start bg-base-300 overflow-x-clip transition-[width] is-drawer-close:w-14 is-drawer-open:w-64"
    style="transition-duration: 300ms"
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
        <button
          class="transition-colors is-drawer-close:tooltip is-drawer-close:tooltip-right"
          style="transition-duration: var(--transition-fast)"
          data-tip="Homepage"
        >
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
          <span class="sidebar-text is-drawer-close:opacity-0">Homepage</span>
        </button>
      </li>

      <li>
        <button
          class="transition-colors is-drawer-close:tooltip is-drawer-close:tooltip-right"
          style="transition-duration: var(--transition-fast)"
          data-tip="Settings"
        >
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
          <span class="sidebar-text is-drawer-close:opacity-0">Settings</span>
        </button>
      </li>
    </ul>

    <!-- 底部用户信息 -->
    <!--
      is-drawer-close:p-0：折叠时去掉 padding
      之前 p-2 在折叠时让按钮偏移 8px，配合 overflow-x-clip 导致右侧 8px 被裁掉
      现在折叠时 padding=0，btn-square(56px) 刚好填满 sidebar(56px)
    -->
    <div class="w-full p-2 is-drawer-close:p-0">
      <div class="mb-2 w-full">
        <button
          ref="userBtnRef"
          @click="toggleUserMenu"
          class="btn btn-ghost w-full justify-start h-14 is-drawer-close:btn-square is-drawer-close:justify-center is-drawer-close:p-0"
        >
          <div class="flex items-center gap-3 is-drawer-close:gap-0">
            <img src="/fcb.svg" class="size-8 shrink-0" alt="avatar" />
            <div
              class="sidebar-text is-drawer-close:opacity-0 is-drawer-close:w-0 flex items-center gap-2"
            >
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
        </button>
      </div>
    </div>

    <!--
      Teleport：把 dropdown 菜单传送到 <body> 层级
      这样它完全脱离了 sidebar 和 drawer-side 的 overflow 上下文
      无论 sidebar 是展开还是折叠，菜单都能正常显示在顶层

      位置通过 JS 动态计算（基于触发按钮的 getBoundingClientRect）
      z-[60]/z-[70] 确保在 DaisyUI drawer 的 z-index 之上
    -->
    <Teleport to="body">
      <!-- 透明遮罩：点击任意空白区域关闭菜单 -->
      <div v-if="isDropdownOpen" class="fixed inset-0 z-[60]" @click="isDropdownOpen = false"></div>
      <!-- 弹出菜单，带淡入/滑出动画 -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-1"
      >
        <ul
          v-if="isDropdownOpen"
          :style="menuStyle"
          class="fixed menu rounded-box bg-base-100 shadow-lg p-2 z-[70]"
        >
          <li class="menu-title">{{ authStore.user?.email }}</li>
          <li><button disabled>Settings</button></li>
          <li><button disabled>Language</button></li>
          <div class="divider my-0"></div>
          <li>
            <button @click="handleLogout" class="font-bold">Log out</button>
          </li>
        </ul>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { userAuthStore } from '@/stores/auth'

const authStore = userAuthStore()

// ===== 用户菜单 dropdown =====
const userBtnRef = ref<HTMLElement>()
const isDropdownOpen = ref(false)
const menuStyle = ref<Record<string, string>>({})

/**
 * 切换用户菜单显示/隐藏
 * 打开时：读取按钮位置，计算菜单应该出现在哪里
 * bottom: 视口高度 - 按钮顶部 + 8px 间距 → 菜单出现在按钮正上方
 * left: 按钮左边缘 → 菜单左对齐按钮
 * minWidth: 至少 192px（min-w-48），或按钮宽度（取大值）
 */
function toggleUserMenu() {
  if (!isDropdownOpen.value && userBtnRef.value) {
    const rect = userBtnRef.value.getBoundingClientRect()
    menuStyle.value = {
      bottom: `${window.innerHeight - rect.top + 8}px`,
      left: `${rect.left}px`,
      minWidth: `${Math.max(rect.width, 192)}px`,
    }
  }
  isDropdownOpen.value = !isDropdownOpen.value
}

function handleLogout() {
  isDropdownOpen.value = false
  setTimeout(() => authStore.logout(), 500)
}
</script>
