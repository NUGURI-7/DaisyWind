import { ref, type Ref } from 'vue'
import { toast } from 'vue-sonner'
import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from "axios";
import type Result from './Result';


const axiosConfig = {
  baseURL: "http://127.0.0.1:8000/api/nuguri/v1",
  withCredentials: false,
  timeout: 1800000, // 30分钟 timeout
  headers: {},
}

const instance = axios.create(axiosConfig)

/* 设置请求拦截器 */
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (config.headers === undefined) {
      config.headers = new AxiosHeaders()
    }
    if (config.url && config.url.startsWith('http')) {
      return config
    }
    const token = localStorage.getItem('token')
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (err: unknown) => {
    return Promise.reject(err)
  },
)


//设置响应拦截器
instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {

        if (response.config.url.includes('/user/login') || response.config.url?.includes('/user/register')) {
          return Promise.reject(response.data)
        }

        toast.error(response.data.message || '请求失败')
        return Promise.reject(response.data)
      }
    }
    return response
  },
  (err: any) => {
    if (err.code === 'ECONNABORTED') {
        toast.error('请求超时，请重试')
    } else if (!err.response) {
      // 没有响应说明网络有问题
        toast.error('网络连接失败')
    } else {
      // HTTP 状态码错误
      const status = err.response.status
      if (status === 401) {
        // token 过期
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else if (status === 500) {
        toast.error('服务器错误')
      } else {
				toast.error(`请求错误 (${status})`)
			}
    }
    return Promise.reject(err)
  }
)

export const request = instance

/** 统一处理返回结果，并增加loading处理，{success,data,message}的格式的返回值为例 */

const promise = (
	request: Promise<any>,
	loading?: Ref<boolean>
): Promise<Result<any>> => {
	return new Promise((resolve, reject)=>{
		if (loading) loading.value = true
		request
			.then((response)=>{
				if (response.status === 200){
					resolve(response?.data || response)
				} else {
					reject(response?.data || response)
				}
			})
			.catch((error) => {
				reject(error)
			})
			.finally(() => {
				if (loading) loading.value = false
			})
	})
}


export const get: (
  url: string,
  params?: unknown,
  loading?: Ref<boolean>,
  timeout?: number,
) => Promise<Result<any>> = (
  url: string,
  params?: unknown,
  loading?: Ref<boolean>,
  timeout?: number,
) => {
    return promise(request({ url: url, method: 'get', params, timeout: timeout }), loading)
  }

export const post: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: Ref<boolean>,
  timeout?: number,
) => Promise<Result<any> | any> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'post', data, params, timeout }), loading)
}

export const put: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: Ref<boolean>,
  timeout?: number,
) => Promise<Result<any>> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'put', data, params, timeout }), loading)
}

export const del: (
  url: string,
  params?: unknown,
  data?: unknown,
  loading?: Ref<boolean>,
  timeout?: number,
) => Promise<Result<any>> = (url, params, data, loading, timeout) => {
  return promise(request({ url: url, method: 'delete', params, data, timeout }), loading)
}