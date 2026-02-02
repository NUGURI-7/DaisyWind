import type { RouteRecordRaw } from "vue-router";




export const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        children: [
            {
                path: 'index',
                component: ()=> import('@/views/home-page/index.vue')
            },
        ]
    }
]