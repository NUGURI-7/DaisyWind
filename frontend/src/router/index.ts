import { createRouter, createWebHistory } from 'vue-router'

import { routes } from './routes'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

const WHITE_LIST = ['/login', '/register']

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')

  if (WHITE_LIST.includes(to.path)) {
    if (token) {
      next('/')
    } else {
      next()
    }
  } else {
    if (!token) {
      next('/login')
    } else {
      next()
    }
  }
})



export default router
