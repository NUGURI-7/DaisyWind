<template>
  <div class="flex flex-col h-screen bg-background overflow-hidden text-foreground">
    <div class="flex items-center px-6 h-14 animate-fade-in">
      <div class="flex items-center">
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

          <!-- 标题带 animate-slide-up + stagger-1 -->
          <h1 class="text-2xl font-bold text-center animate-slide-up stagger-1 tracking-tight">
            Create an Account
          </h1>

          <Card
            class="bg-card/70 backdrop-blur-md shadow-lg border-border mb-26 animate-scale-in stagger-2 transition-shadow hover:shadow-xl"
            style="transition-duration: var(--transition-normal)"
          >
            <CardContent class="p-6 space-y-4">
              <form @submit.prevent="handleRegister" class="space-y-4">
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
                  <Label for="nick_name">Nickname</Label>
                  <Input
                    id="nick_name"
                    v-model="form.nick_name"
                    type="text"
                    placeholder="Enter your nickname"
                    class="w-full transition-colors"
                    style="transition-duration: var(--transition-fast)"
                    required
                    maxlength="30"
                  />
                </div>
                <div class="space-y-1.5 animate-slide-up stagger-4">
                  <Label for="email">Email</Label>
                  <Input
                    id="email"
                    v-model="form.email"
                    type="email"
                    placeholder="Enter your email"
                    class="w-full transition-colors"
                    style="transition-duration: var(--transition-fast)"
                    required
                  />
                </div>
                <div class="space-y-1.5 animate-slide-up stagger-5">
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

                <p v-if="errorMsg" class="text-destructive text-sm text-center animate-slide-down">
                  {{ errorMsg }}
                </p>

                <Button
                  type="submit"
                  class="w-full animate-slide-up stagger-5 transition-all hover:-translate-y-0.5 hover:shadow-md cursor-pointer"
                  style="transition-duration: var(--transition-fast)"
                  :disabled="loading"
                >
                  <PhSpinner v-if="loading" class="animate-spin mr-2" />
                  <span v-else>Sign up</span>
                </Button>
              </form>

              <div class="relative flex items-center py-2">
                <div class="flex-1"><Separator /></div>
                <span class="mx-4 text-xs text-muted-foreground">or</span>
                <div class="flex-1"><Separator /></div>
              </div>
              <p class="text-center text-sm animate-fade-in stagger-5 text-muted-foreground">
                Already have an account?
                <router-link to="/login" class="font-medium text-primary hover:underline underline-offset-2">
                  Sign in
                </router-link>
              </p>
            </CardContent>
          </Card>
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
