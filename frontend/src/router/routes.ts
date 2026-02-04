import type { RouteRecordRaw } from "vue-router";




export const routes: Array<RouteRecordRaw> = [
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