import { useStorage } from "@vueuse/core";
import { watch } from "vue";


export function userTheme() {
  const theme = useStorage('theme','cupcake')

  const applyTheme = (themeName: string) => {
    document.documentElement.setAttribute('data-theme', themeName)
  }
  // 初始化
  applyTheme(theme.value)

  watch(theme, (newTheme) => {
    applyTheme(newTheme)
  })

  const setTheme = (themeName: string) => {
    theme.value = themeName
  }

  const toggleTheme = (themeName: string) => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  const themes = [
    'light',
    'dark',
    'cupcake',
    'bumblebee',
    'emerald',
    'corporate',
    'synthwave',
    'retro',
    'cyberpunk',
    'valentine',
    'halloween',
    'garden',
    'forest',
    'aqua',
    'lofi',
    'pastel',
    'fantasy',
    'wireframe',
    'black',
    'luxury',
    'dracula',
    'cmyk',
    'autumn',
    'business',
    'acid',
    'lemonade',
    'night',
    'coffee',
    'winter',
    'dim',
    'nord',
    'sunset',
  ]

  return {
    theme,
    setTheme,
    toggleTheme,
    themes,
  }


}