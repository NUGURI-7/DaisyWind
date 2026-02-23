<template>
  <div class="flex flex-col h-screen bg-base-100 overflow-hidden">
    <div class="navbar px-6 animate-fade-in">
      <div class="navbar-start">
        <img src="/claude-icon.svg" class="mr-2 size-8" alt="logo" />
        <span class="text-2xl font-bold tracking-tight">DaisyWind</span>
      </div>
    </div>
    <div class="flex flex-col lg:flex-row flex-1 min-h-0 w-full px-6">
      <div class="w-full lg:w-1/2 flex items-center justify-center overflow-y-auto min-h-0 px-6">
        <div class="w-full max-w-sm space-y-6">
          <div class="flex items-center justify-center gap-12 mb-6">
            <img
              src="/mark-rotating.svg"
              class="size-10 animate-slide-up animate-gentle-float"
              alt="mark"
            />
            <img
              src="/tailwind-icon.svg"
              class="size-10 animate-slide-up animate-gentle-float stagger-1"
              alt="tailwind"
            />
          </div>

          <!-- 保留 🌸 emoji -->
          <h1 class="text-2xl font-bold text-center animate-slide-up stagger-1">
            Create Account 🌸
          </h1>

          <div
            class="card bg-base-200/70 backdrop-blur-md shadow-2xl border border-base-300/50 mb-26 animate-scale-in stagger-2 transition-shadow hover:shadow-[0_8px_30px_rgba(0,0,0,0.08)]"
            style="transition-duration: var(--transition-normal)"
          >
            <div class="card-body p-6 space-y-4">
              <form @submit.prevent="handleRegister" class="space-y-4">
                <!--
                  Register 有 4 个字段，stagger 从 2 到 5
                  每个间隔 80ms，4 个字段总共 320ms 的交错时间
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
                  <legend class="fieldset-legend">Nickname</legend>
                  <input
                    v-model="form.nick_name"
                    type="text"
                    placeholder="Enter your nickname"
                    class="input input-bordered w-full transition-colors focus:border-base-content/30"
                    style="transition-duration: var(--transition-fast)"
                    required
                    maxlength="30"
                  />
                </fieldset>
                <fieldset class="fieldset animate-slide-up stagger-4">
                  <legend class="fieldset-legend">Email</legend>
                  <input
                    v-model="form.email"
                    type="email"
                    placeholder="Enter your email"
                    class="input input-bordered w-full transition-colors focus:border-base-content/30"
                    style="transition-duration: var(--transition-fast)"
                    required
                  />
                </fieldset>
                <fieldset class="fieldset animate-slide-up stagger-5">
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

                <p v-if="errorMsg" class="text-error text-sm text-center animate-slide-down">
                  {{ errorMsg }}
                </p>

                <button
                  type="submit"
                  class="btn btn-neutral btn-block animate-slide-up stagger-5 transition-all hover:-translate-y-0.5 hover:shadow-lg"
                  style="transition-duration: var(--transition-fast)"
                  :disabled="loading"
                >
                  <span v-if="loading" class="loading loading-spinner loading-sm"></span>
                  <span v-else>Sign up</span>
                </button>
              </form>

              <div class="divider my-0 text-xs text-base-content/40">or</div>
              <p class="text-center text-sm animate-fade-in stagger-5">
                Already have an account?
                <router-link to="/login" class="link link-hover font-medium underline-offset-2">
                  Sign in
                </router-link>
              </p>
            </div>
          </div>
        </div>
      </div>

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
  nick_name: '',
  email: '',
  password: '',
})

const loading = ref(false)
const errorMsg = ref('')
const usernameRegex = /^[a-zA-Z0-9_-]+$/

async function handleRegister() {
  errorMsg.value = ''

  if (!usernameRegex.test(form.username)) {
    errorMsg.value = 'Username can only contain letters, numbers, underscores and hyphens'
    return
  }

  loading.value = true

  try {
    await authStore.register(form.username, form.nick_name, form.email, form.password)
    toast.success('Registration successful, please sign in')
    setTimeout(() => router.push('/login'), 1500)
  } catch (err: any) {
    errorMsg.value = err?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
