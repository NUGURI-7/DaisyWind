import type { RouteRecordRaw } from "vue-router";




export const routes: Array<RouteRecordRaw> = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/login/index.vue')
    },
    {
        path: '/register',
        name: 'register',
        component: () => import('@/views/register/index.vue')
    },
    {
        path: '/',
        name: 'home',
        redirect: 'chat',
        component: ()=> import('@/layout/AppLayout.vue'),
        children: [
            {
                path: 'chat',
                component: ()=> import('@/views/chat/index.vue')
            },
        ]
    }
]