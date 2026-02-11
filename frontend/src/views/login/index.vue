<template>
  <div class="flex flex-col h-screen bg-base-100 overflow-hidden">
    <!-- 导航栏 -->
    <div class="navbar px-6">
      <div class="navbar-start">
        <span class="text-xl font-bold tracking-tight"> DaisyWind </span>
      </div>
    </div>
    <!-- 主体：左右分栏 -->
    <div class="flex flex-col justify-center items-center w-full lg:w-1/2 px-6">
      <!-- 左侧 -->
      <div class="flex flex-1 justify-center items-center w-full lg:w-1/2 px-6">
        <div class="w-full max-w-sm space-y-8">
          <!-- 标题 -->
          <h1 class="text-3xl font-bold text-center">Welcome DaisyWind 🌼</h1>
          <!-- 表单 -->
          <form @submit.prevent="handleLogin" class="space-y-4">
            <fieldset class="fieldset">
              <legend class="fieldset-legend">Username</legend>
              <input
                v-model="form.username"
                type="text"
                placeholder="Enter your username"
                class="input input-bordered w-full"
                required
                minlength="3"
                maxlength="20"
              />
            </fieldset>
            <fieldset class="fieldset">
              <legend class="fieldset-legend">Password</legend>
              <input
                v-model="form.password"
                type="password"
                placeholder="Enter your password"
                class="input input-bordered w-full"
                required
                minlength="6"
                maxlength="50"
              />
            </fieldset>
            <p v-if="errorMsg" class="text-error text-sm text-center">{{ errorMsg }}</p>

            <button type="submit" class="btn btn-neutral btn-block" :disabled="loading">
              <span v-if="loading" class="loading loading-spinner loading-sm"></span>
              <span v-else> Sign in</span>
            </button>
          </form>
          <!-- 底部跳转 -->

          <p class="text-center text-sm">
            Don't have an account?
            <router-link to="/register" class="link link-hover font-medium"> Sign up </router-link>
          </p>
        </div>
        <!-- 右侧图片 移动端隐藏 -->
        <div class="hidden lg:flex lg:w-1/2 items-center justify-center p-8">
          <video
            src="https://claude.ai/images/home-page-assets/videos/claude_login_v2.mp4"
            autoplay
            loop
            playsinline
            class="w-full h-full object-cover rounded-2xl shadow-[0_4px_20px_0_hsl(var(--always-black)/4%)]"
            style="object-position: 80% 20%"
          ></video>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { userAuthStore } from '@/stores/auth'

const router = useRouter()

const authStore = userAuthStore()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  errorMsg.value = ''
  loading.value = true

  try {
    await authStore.login(form.username, form.password)
    router.push('/')
  } catch (err: any) {
    errorMsg.value = err?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
