<template>
  <!--
    Bug fix 说明：
    1. overflow-hidden → overflow-x-clip
       overflow-x-clip 只裁剪水平溢出（折叠动画需要），垂直方向不受影响
       这样 dropdown 可以向上弹出不被裁剪
       （注意：overflow-x: clip 和 overflow-x: hidden 的关键区别是
        clip 可以独立控制单轴，hidden 会把另一轴也变成 auto/scroll）
    2. 底部容器 
       折叠时去掉 padding，让 btn-square 正好填满 56px 宽度
       之前 p-2（8px×2）让按钮从 8px 开始，56px 的按钮会溢出被裁掉 8px
    3. dropdown 用 <Teleport to="body"> 完全脱离 sidebar 的 overflow 上下文
       不再受任何祖先容器的 overflow 影响
  -->
  <aside
    :data-collapsed="!isOpen ? '' : undefined"
    class="group/sidebar flex min-h-full flex-col bg-sidebar overflow-x-clip transition-[width] data-[collapsed]:w-14 w-64 border-r border-sidebar-border"
    style="transition-duration: 300ms"
  >
    <!-- 顶部栏：图标始终锚定左侧，toggle 按钮在右侧，sidebar 向右扩展 -->
    <div class="w-full flex items-center h-14 px-3 gap-3 shrink-0">
      <!-- logo：折叠时 hover 变为展开图标，位置不动 -->
      <div class="relative group shrink-0">
        <img
          src="/claude-icon.svg"
          class="w-8 transition-opacity duration-200 group-data-[collapsed]/sidebar:group-hover:opacity-0"
          alt="logo"
        />
        <button
          @click="$emit('toggle')"
          aria-label="open sidebar"
          class="absolute inset-0 flex items-center justify-center opacity-0 pointer-events-none transition-opacity duration-200 cursor-pointer text-sidebar-foreground group-data-[collapsed]/sidebar:group-hover:opacity-100 group-data-[collapsed]/sidebar:group-hover:pointer-events-auto"
        >
          <PhSidebarSimple :size="20" />
        </button>
      </div>

      <span
        class="font-bold text-lg tracking-tight text-sidebar-foreground max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap"
      >
        DaisyWind
      </span>

      <!-- 展开时右侧的收起按钮，ml-auto 推到最右 -->
      <button
        @click="$emit('toggle')"
        aria-label="close sidebar"
        class="ml-auto shrink-0 flex items-center justify-center size-8 text-sidebar-foreground rounded-md hover:bg-sidebar-accent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring/50 cursor-pointer max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out"
      >
        <PhSidebarSimple :size="20" />
      </button>
    </div>

    <nav class="flex flex-col w-full grow px-2 gap-1 mt-4">
      <TooltipProvider :delay-duration="100">
        <!-- New Chat -->
        <Tooltip>
          <TooltipTrigger as-child>
            <RouterLink
              v-slot="{ isActive }"
              to="/chat"
              custom
            >
              <button
                @click="$router.push('/chat')"
                class="flex items-center w-full h-10 px-2 gap-3 rounded-md text-sm font-medium transition-colors "
                :class="isActive
                  ? 'text-primary font-semibold'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'"
                :style="{ transitionDuration: 'var(--transition-fast)' }"
              >
                <PhPlus :size="18" class="shrink-0" />
                <span
                  class="sidebar-text max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap"
                >
                  New Chat
                </span>
              </button>
            </RouterLink>
          </TooltipTrigger>
          <TooltipContent side="right" :side-offset="8" v-if="!isOpen"> New Chat </TooltipContent>
        </Tooltip>

        <!-- Notes -->
        <Tooltip>
          <TooltipTrigger as-child>
            <RouterLink
              v-slot="{ isActive }"
              to="/notes"
              custom
            >
              <button
                @click="$router.push('/notes')"
                class="flex items-center w-full h-10 px-2 gap-3 rounded-md text-sm font-medium transition-colors "
                :class="isActive
                  ? 'text-primary font-semibold'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'"
                :style="{ transitionDuration: 'var(--transition-fast)' }"
              >
                <PhNotePencil :size="18" class="shrink-0" />
                <span
                  class="sidebar-text max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap"
                >
                  Notes
                </span>
              </button>
            </RouterLink>
          </TooltipTrigger>
          <TooltipContent side="right" :side-offset="8" v-if="!isOpen"> Notes </TooltipContent>
        </Tooltip>

        <!-- Settings (Theme Switcher) -->
        <Popover>
          <PopoverTrigger as-child>
            <button
              class="flex items-center w-full h-10 px-2 gap-3 rounded-md text-sm font-medium text-sidebar-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground  cursor-pointer"
              :style="{ transitionDuration: 'var(--transition-fast)' }"
            >
              <PhSliders :size="18" class="shrink-0" />
              <span
                class="sidebar-text max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out overflow-hidden whitespace-nowrap"
              >
                Settings
              </span>
            </button>
          </PopoverTrigger>
          <PopoverContent side="right" :side-offset="12" align="end" class="p-0 w-auto">
            <ThemeSwitcher />
          </PopoverContent>
        </Popover>
      </TooltipProvider>
    </nav>

    <!-- 底部用户信息 -->
    <!--
      ：折叠时去掉 padding
      之前 p-2 在折叠时让按钮偏移 8px，配合 overflow-x-clip 导致右侧 8px 被裁掉
      现在折叠时 padding=0，btn-square(56px) 刚好填满 sidebar(56px)
    -->
    <div class="w-full p-2 ">
      <div class="w-full">
        <button
          ref="userBtnRef"
          @click="toggleUserMenu"
          class="flex items-center w-full h-12 px-2 gap-3 rounded-md text-sidebar-foreground hover:bg-sidebar-accent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring/50 "
        >
          <img src="/fcb.svg" class="size-7 shrink-0 object-contain" alt="avatar" />
          <div
            class="flex flex-col items-start text-left overflow-hidden max-w-[200px] group-data-[collapsed]/sidebar:max-w-0 group-data-[collapsed]/sidebar:opacity-0 transition-all duration-300 ease-in-out"
          >
            <span class="text-sm font-medium leading-none whitespace-nowrap">
              {{ authStore.user?.nick_name || 'User' }}
            </span>
            <span class="text-xs text-muted-foreground mt-1 whitespace-nowrap">
              {{ authStore.user?.email || 'admin@daisywind.com' }}
            </span>
          </div>
        </button>
      </div>
    </div>

    <!--
      Teleport：把 dropdown 菜单传送到 <body> 层级
      这样它完全脱离了 sidebar 和其他布局组件的 overflow 上下文
      无论 sidebar 是展开还是折叠，菜单都能正常显示在顶层

      位置通过 JS 动态计算（基于触发按钮的 getBoundingClientRect）
      z-60/z-70 确保浮层在 sidebar 之上
    -->
    <Teleport to="body">
      <!-- 透明遮罩：点击任意空白区域关闭菜单 -->
      <div v-if="isDropdownOpen" class="fixed inset-0 z-60" @click="isDropdownOpen = false"></div>
      <!-- 弹出菜单，带淡入/滑出动画 -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 translate-y-1"
      >
        <div
          v-if="isDropdownOpen"
          :style="menuStyle"
          class="fixed flex flex-col rounded-md bg-popover shadow-md border border-border text-popover-foreground p-1 z-70"
        >
          <li class="text-xs text-muted-foreground px-2 py-1.5">{{ authStore.user?.email }}</li>
          <button
            class="w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded-sm disabled:opacity-50"
            disabled
          >
            Settings
          </button>
          <button
            class="w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded-sm disabled:opacity-50"
            disabled
          >
            Language
          </button>
          <div class="h-px bg-border my-1 w-full shrink-0"></div>
          <div class="flex flex-col gap-1.5 py-1 px-3">
            <div class="flex items-center gap-2">
              <PhAirplaneTakeoff :size="12" class="text-muted-foreground/70 shrink-0" />

              <span class="text-xs text-muted-foreground/70">Login count</span>
              <span class="ml-auto text-xs font-medium text-sidebar-foreground/70">{{
                authStore.user?.login_count
              }}</span>
            </div>
            <div class="flex items-center gap-2">
              <PhClock :size="12" class="text-muted-foreground/70 shrink-0" />
              <span class="text-xs text-muted-foreground/70">Last login</span>
              <span class="ml-auto text-xs font-medium text-sidebar-foreground/70">{{
                fromNow(authStore.user?.last_login)
              }}</span>
            </div>
          </div>

          <div class="h-px bg-border my-1 w-full shrink-0"></div>
          <button
            @click="handleLogout"
            class="w-full text-left px-3 py-1.5 text-sm font-medium text-destructive hover:bg-muted rounded-sm"
          >
            Log out
          </button>
        </div>
      </Transition>
    </Teleport>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'

defineProps<{
  isOpen: boolean
}>()

defineEmits(['toggle'])
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { PhAirplaneTakeoff, PhClock } from '@phosphor-icons/vue'
import { RouterLink } from 'vue-router'
import { userAuthStore } from '@/stores/auth'
import { PhSidebarSimple, PhNotePencil, PhSliders, PhPlus } from '@phosphor-icons/vue'

const authStore = userAuthStore()

dayjs.extend(relativeTime)
const fromNow = (date: any) => (date ? dayjs(date).fromNow() : 'Never')

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
