import { get, post } from '@/request'
import type { Ref } from 'vue'


/**
 * 登录
 */
const postLogin = (
  data: {
    username: string;
    password: string
  },
  loading?: Ref<boolean>
) => {
  return post('/user/login', data,undefined, loading)
}

/**
 * 注册
 */

const postRegister = (
  data: {
    username: string,
    email: string,
    nick_name: string,
    password: string
  },
  loading?: Ref<boolean>

) => {
  return post('/user/register', data, undefined, loading)
}

/** 
 * 获取当前用户 
 * */

const getCurrentUser = (loading?: Ref<boolean>) => {
  return get('/user/current_user', undefined, loading)
}


export default {
  postLogin,
  postRegister,
  getCurrentUser
}