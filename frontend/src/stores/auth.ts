import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { useRouter } from "vue-router"
import userApi from '@/api/user'



export interface UserInfo { 
  uuid: string
  username: string
  nick_name: string
  rank_title: string
  email: string
  is_admin: boolean
  created_at: string
  updated_at: string
}

export const userAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)
  
  /**
   * 登录
   */
  async function login(username:string, password: string) {
    const res =  await userApi.postLogin({username, password})
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
  } 

  /**
   * 注册
   */
  async function register(username: string, nick_name: string,email: string, password: string) {
    await userApi.postRegister({username, nick_name,email, password})
  }

  /**
   * 获取当前用户信息
   */
  async function fetchCurrentUser() {
    const res = await userApi.getCurrentUser()
    user.value = res.data
  }

  /**
   * 登出
   */
  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, user, isAuthenticated, login, register, fetchCurrentUser,logout }


})



