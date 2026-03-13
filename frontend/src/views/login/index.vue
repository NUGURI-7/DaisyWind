<template>
  <div class="flex flex-col h-screen bg-background overflow-hidden text-foreground">
    <!-- 导航栏：加 animate-fade-in 入场 -->
    <div class="flex items-center px-6 h-14 animate-fade-in">
      <div class="flex items-center">
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

          <!-- 标题带 animate-slide-up + stagger-1 -->
          <h1 class="text-2xl font-bold text-center animate-slide-up stagger-1 tracking-tight">
            Welcome to DaisyWind
          </h1>

          <!--
            卡片：animate-scale-in + stagger-2
            从 0.95 缩放弹入，配合 stagger 延迟，在标题之后出现
            hover 时 shadow 稍微增大，有"浮起来"的感觉
          -->
          <Card
            class="bg-card/70 backdrop-blur-md shadow-lg border-border mb-26 animate-scale-in stagger-2 transition-shadow hover:shadow-xl"
            style="transition-duration: var(--transition-normal)"
          >
            <CardContent class="p-6 space-y-4">
              <form @submit.prevent="handleLogin" class="space-y-4">
                <!--
                  每个 fieldset 加 animate-slide-up + 递增的 stagger
                  表单字段逐个从下方滑入，有交错节奏感
                -->
                <div class="space-y-1.5 animate-slide-up stagger-2">
                  <Label for="username">Username</Label>
                  <Input
                    id="username"
                    v-model="form.username"
                    type="text"
                    placeholder="Enter your username"
                    class="w-full transition-colors"
                    style="transition-duration: var(--transition-fast)"
                    required
                    minlength="3"
                    maxlength="20"
                    pattern="[a-zA-Z0-9_\-]+"
                    title="Only letters, numbers, underscores and hyphens"
                  />
                </div>
                <div class="space-y-1.5 animate-slide-up stagger-3">
                  <Label for="password">Password</Label>
                  <Input
                    id="password"
                    v-model="form.password"
                    type="password"
                    placeholder="Enter your password"
                    class="w-full transition-colors"
                    style="transition-duration: var(--transition-fast)"
                    required
                    minlength="6"
                    maxlength="50"
                  />
                </div>

                <!-- 错误消息：animate-slide-down 从上方滑入 -->
                <p v-if="errorMsg" class="text-destructive text-sm text-center animate-slide-down">
                  {{ errorMsg }}
                </p>

                <!--
                  提交按钮：animate-slide-up stagger-4
                  hover 时 微弱上移 + 加阴影，有"按钮被抬起来"的感觉
                -->
                <Button
                  type="submit"
                  class="w-full animate-slide-up stagger-4 transition-all hover:-translate-y-0.5 hover:shadow-md cursor-pointer"
                  style="transition-duration: var(--transition-fast)"
                  :disabled="loading"
                >
                  <PhSpinner v-if="loading" class="animate-spin mr-2" />
                  <span v-else>Sign in</span>
                </Button>
              </form>

              <!-- 分割线 + 跳转链接 -->
              <div class="relative flex items-center py-2">
                <div class="flex-1"><Separator /></div>
                <span class="mx-4 text-xs text-muted-foreground">or</span>
                <div class="flex-1"><Separator /></div>
              </div>
              <p class="text-center text-sm animate-fade-in stagger-5 text-muted-foreground">
                Don't have an account?
                <router-link to="/register" class="font-medium text-primary hover:underline underline-offset-2">
                  Sign up
                </router-link>
              </p>
            </CardContent>
          </Card>
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
          class="max-w-full mb-14 max-h-full object-cover rounded-2xl shadow-xl border border-border"
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
import { PhSpinner } from '@phosphor-icons/vue'

import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'

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
