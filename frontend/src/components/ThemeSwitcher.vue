<template>
  <div class="flex flex-col gap-4 p-4 w-64">
    <!-- Theme 选择 -->
    <div>
      <h4 class="text-xs font-medium text-muted-foreground mb-2.5 uppercase tracking-wider">
        Theme
      </h4>
      <div class="grid grid-cols-6 gap-2">
        <button
          v-for="opt in THEME_OPTIONS"
          :key="opt.name"
          @click="setTheme(opt.name)"
          class="group relative flex items-center justify-center size-8 rounded-full border-2 transition-all duration-200 cursor-pointer hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
          :class="
            theme === opt.name
              ? 'border-foreground shadow-sm'
              : 'border-transparent hover:border-border'
          "
          :title="opt.label"
        >
          <span
            class="size-5 rounded-full"
            :style="{ backgroundColor: opt.swatch }"
          />
          <!-- Check mark -->
          <PhCheck
            v-if="theme === opt.name"
            :size="10"
            weight="bold"
            class="absolute text-primary-foreground"
            :style="{ color: contrastColor(opt.swatch) }"
          />
        </button>
      </div>
    </div>

    <!-- 分割线 -->
    <div class="h-px bg-border" />

    <!-- Light / Dark 切换 -->
    <div>
      <h4 class="text-xs font-medium text-muted-foreground mb-2.5 uppercase tracking-wider">
        Mode
      </h4>
      <div class="flex gap-1 p-0.5 bg-muted rounded-md">
        <button
          @click="setDark(false)"
          class="flex-1 flex items-center justify-center gap-1.5 h-7 rounded text-xs font-medium transition-all duration-200 cursor-pointer"
          :class="
            !isDark
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          "
        >
          <PhSun :size="14" />
          Light
        </button>
        <button
          @click="setDark(true)"
          class="flex-1 flex items-center justify-center gap-1.5 h-7 rounded text-xs font-medium transition-all duration-200 cursor-pointer"
          :class="
            isDark
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          "
        >
          <PhMoon :size="14" />
          Dark
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PhCheck, PhSun, PhMoon } from '@phosphor-icons/vue'
import { useTheme, THEME_OPTIONS } from '@/composables/useTheme'

const { theme, isDark, setTheme, setDark } = useTheme()

/** 根据 oklch 亮度决定 check mark 颜色 */
function contrastColor(oklch: string): string {
  const match = oklch.match(/oklch\(([\d.]+)/)
  const lightness = match ? parseFloat(match[1]!) : 0.5
  return lightness > 0.6 ? 'oklch(0.2 0 0)' : 'oklch(0.98 0 0)'
}
</script>
