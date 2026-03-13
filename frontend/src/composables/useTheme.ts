import { ref } from 'vue'

// ── 主题定义 ──────────────────────────────────────────────────
export type ThemeName =
  | 'stone'
  | 'neutral'
  | 'zinc'
  | 'gray'
  | 'slate'
  | 'rose'
  | 'red'
  | 'orange'
  | 'green'
  | 'blue'
  | 'yellow'
  | 'violet'

export interface ThemeOption {
  name: ThemeName
  label: string
  /** 用于色块预览的 oklch 色值（light mode 的 --primary） */
  swatch: string
}

export const THEME_OPTIONS: ThemeOption[] = [
  // Gray-scale bases（改变整体灰色调）
  { name: 'stone', label: 'Stone', swatch: 'oklch(0.216 0.006 56.043)' },
  { name: 'neutral', label: 'Neutral', swatch: 'oklch(0.205 0 0)' },
  { name: 'zinc', label: 'Zinc', swatch: 'oklch(0.21 0.006 285.885)' },
  { name: 'gray', label: 'Gray', swatch: 'oklch(0.21 0.034 264.665)' },
  { name: 'slate', label: 'Slate', swatch: 'oklch(0.208 0.042 265.755)' },
  // Colorful accents（只改变 primary / ring）
  { name: 'rose', label: 'Rose', swatch: 'oklch(0.585 0.22 17.5)' },
  { name: 'red', label: 'Red', swatch: 'oklch(0.577 0.245 27.325)' },
  { name: 'orange', label: 'Orange', swatch: 'oklch(0.705 0.213 47.604)' },
  { name: 'green', label: 'Green', swatch: 'oklch(0.527 0.185 150.069)' },
  { name: 'blue', label: 'Blue', swatch: 'oklch(0.623 0.214 259.815)' },
  { name: 'yellow', label: 'Yellow', swatch: 'oklch(0.795 0.184 86.047)' },
  { name: 'violet', label: 'Violet', swatch: 'oklch(0.606 0.25 292.717)' },
]

// ── 持久化 key ────────────────────────────────────────────────
const STORAGE_THEME = 'dw-theme'
const STORAGE_DARK = 'dw-dark'

// ── 全局响应式状态（单例，多处 useTheme() 共享） ──────────────
const theme = ref<ThemeName>(
  (localStorage.getItem(STORAGE_THEME) as ThemeName) || 'stone',
)
const isDark = ref(localStorage.getItem(STORAGE_DARK) === 'true')

// ── 应用到 DOM ────────────────────────────────────────────────
function applyTheme() {
  const el = document.documentElement

  // 清除旧的 theme-* 和 dark class
  const classes = el.className
    .split(/\s+/)
    .filter((c) => !c.startsWith('theme-') && c !== 'dark')

  // 添加新的（stone 是默认，不需要额外 class）
  if (theme.value !== 'stone') {
    classes.push(`theme-${theme.value}`)
  }
  if (isDark.value) {
    classes.push('dark')
  }

  el.className = classes.join(' ')
}

// ── 公开 API ──────────────────────────────────────────────────
export function useTheme() {
  function setTheme(name: ThemeName) {
    theme.value = name
    localStorage.setItem(STORAGE_THEME, name)
    applyTheme()
  }

  function toggleDark() {
    isDark.value = !isDark.value
    localStorage.setItem(STORAGE_DARK, String(isDark.value))
    applyTheme()
  }

  function setDark(value: boolean) {
    isDark.value = value
    localStorage.setItem(STORAGE_DARK, String(value))
    applyTheme()
  }

  return { theme, isDark, setTheme, toggleDark, setDark, applyTheme }
}
