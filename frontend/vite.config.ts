import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // ldrs 的所有 web component 都以 l- 开头（l-miyagi / l-ring / l-dot-pulse 等）
          isCustomElement: (tag) => tag.startsWith('l-'),
        },
      },
    }),
    vueDevTools(),
    tailwindcss(),
  ],
  server: {
    cors: true,
    host: '0.0.0.0', // 修改：允许内网访问
    port: 7777,
    strictPort: true,
    // 修改：增加代理配置，解决内网访问时 API 请求报错的问题
    // 将包含 /api 的请求转发到后端的 8000 端口
    // （如果你的后端实际运行在 7999 端口，请将下面的 8000 改为 7999）
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7999',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    // resolve 必须保留！
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
