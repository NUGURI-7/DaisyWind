import type { RouteRecordRaw } from "vue-router";




export const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        component: ()=> import('@/layout/AppLayout.vue'),
        children: [
            {
                path: 'home',
                component: ()=> import('@/views/home-page/index.vue')
            },
        ]
    }
]