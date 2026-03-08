<template>
  <div class="flex flex-col h-screen bg-base-100 overflow-hidden">
    <!-- 导航栏：加 animate-fade-in 入场 -->
    <div class="navbar px-6 animate-fade-in">
      <div class="navbar-start">
        <img src="/claude-icon.svg" class="mr-2 size-8" alt="logo" />
        <span class="text-2xl font-bold tracking-tight">DaisyWind</span>
      </div>
    </div>
    <!-- 主体：左右分栏 -->
    <div class="flex flex-col lg:flex-row flex-1 min-h-0 w-full px-6">
      <!-- 左侧 -->
      <div class="w-full lg:w-1/2 flex items-center justify-center overflow-y-auto min-h-0 px-6">
        <div class="w-full max-w-sm space-y-6">
          <!-- 单图 logo：保持居中和留白，避免替换大图后视觉失衡 -->
          <div class="mb-4 flex justify-center">
            <div class="flex h-32 w-32 items-center justify-center sm:h-32 sm:w-32">
              <img
                src="/gopher-fcb-glass.png"
                class="h-full w-full object-contain animate-slide-up"
                alt="DaisyWind gopher mascot"
              />
            </div>
          </div>

          <!-- 保留 🌼 emoji，标题带 animate-slide-up + stagger-1 -->
          <h1 class="text-2xl font-bold text-center animate-slide-up stagger-1">
            Welcome DaisyWind 🌼
          </h1>

          <!--
            卡片：animate-scale-in + stagger-2
            从 0.95 缩放弹入，配合 stagger 延迟，在标题之后出现
            hover 时 shadow 稍微增大，有"浮起来"的感觉
          -->
          <div
            class="card bg-base-200/70 backdrop-blur-md shadow-2xl border border-base-300/50 mb-26 animate-scale-in stagger-2 transition-shadow hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)]"
            style="transition-duration: var(--transition-normal)"
          >
            <div class="card-body p-6 space-y-4">
              <form @submit.prevent="handleLogin" class="space-y-4">
                <!--
                  每个 fieldset 加 animate-slide-up + 递增的 stagger
                  表单字段逐个从下方滑入，有交错节奏感

                  input 的 focus 效果：
                  - 去掉 ring（光晕），你觉得太突兀
                  - 只保留 focus:border-base-content/30，聚焦时边框稍微加深
                  - 效果很克制，不抢视觉焦点
                -->
                <fieldset class="fieldset animate-slide-up stagger-2">
                  <legend class="fieldset-legend">Username</legend>
                  <input
                    v-model="form.username"
                    type="text"
                    placeholder="Enter your username"
                    class="input input-bordered w-full transition-colors focus:border-base-content/30"
                    style="transition-duration: var(--transition-fast)"
                    required
                    minlength="3"
                    maxlength="20"
                    pattern="[a-zA-Z0-9_\-]+"
                    title="Only letters, numbers, underscores and hyphens"
                  />
                </fieldset>
                <fieldset class="fieldset animate-slide-up stagger-3">
                  <legend class="fieldset-legend">Password</legend>
                  <input
                    v-model="form.password"
                    type="password"
                    placeholder="Enter your password"
                    class="input input-bordered w-full transition-colors focus:border-base-content/30"
                    style="transition-duration: var(--transition-fast)"
                    required
                    minlength="6"
                    maxlength="50"
                  />
                </fieldset>

                <!-- 错误消息：animate-slide-down 从上方滑入 -->
                <p v-if="errorMsg" class="text-error text-sm text-center animate-slide-down">
                  {{ errorMsg }}
                </p>

                <!--
                  提交按钮：animate-slide-up stagger-4
                  hover 时 微弱上移 + 加阴影，有"按钮被抬起来"的感觉
                  用 transform 做动画（GPU 加速，不会引起 layout shift）
                -->
                <button
                  type="submit"
                  class="btn btn-neutral btn-block animate-slide-up stagger-4 transition-all hover:-translate-y-0.5 hover:shadow-lg"
                  style="transition-duration: var(--transition-fast)"
                  :disabled="loading"
                >
                  <span v-if="loading" class="loading loading-spinner loading-sm"></span>
                  <span v-else>Sign in</span>
                </button>
              </form>

              <!-- 分割线 + 跳转链接，不用 link-primary，用默认文字色 -->
              <div class="divider my-0 text-xs text-base-content/40">or</div>
              <p class="text-center text-sm animate-fade-in stagger-5">
                Don't have an account?
                <router-link to="/register" class="link link-hover font-medium underline-offset-2">
                  Sign up
                </router-link>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!--
        右侧视频：animate-slide-in-right
        从右方 30px 位置滑入，和左侧的 slide-up 形成方向对比
      -->
      <div
        class="hidden lg:flex lg:w-1/2 items-center justify-center overflow-hidden min-h-0 p-8 h-60 lg:h-full animate-slide-in-right"
      >
        <video
          src="https://claude.ai/images/home-page-assets/videos/claude_login_v2.mp4"
          autoplay
          loop
          muted
          playsinline
          class="max-w-full mb-14 max-h-full object-cover rounded-2xl shadow-[0_4px_20px_0_hsl(var(--always-black)/4%)]"
          style="object-position: 80% 20%"
        ></video>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { userAuthStore } from '@/stores/auth'
import { toast } from 'vue-sonner'

const router = useRouter()
const authStore = userAuthStore()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const errorMsg = ref('')
const usernameRegex = /^[a-zA-Z0-9_-]+$/

async function handleLogin() {
  errorMsg.value = ''

  if (!usernameRegex.test(form.username)) {
    errorMsg.value = 'Username can only contain letters, numbers, underscores and hyphens'
    return
  }

  loading.value = true

  try {
    await authStore.login(form.username, form.password)
    toast.success('Login successful', { duration: 1500 })
    router.push('/')
  } catch (err: any) {
    errorMsg.value = err?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
