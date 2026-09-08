import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/views/About.vue')
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/views/Gallery.vue')
  },
  {
    path: '/lucky',
    name: 'LuckyDraw',
    component: () => import('@/views/LuckyDraw.vue')
  },
  {
    path: '/wallpaper',
    name: 'Wallpaper',
    component: () => import('@/views/Wallpaper.vue')
  },
  {
    path: '/tarot',
    name: 'Tarot',
    component: () => import('@/views/Tarot.vue')
  },
  {
    path: '/meme',
    name: 'MemeMaker',
    component: () => import('@/views/MemeMaker.vue')
  },
  {
    path: '/collection',
    name: 'Collection',
    component: () => import('@/views/Collection.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue')
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('@/views/Quiz.vue')
  },
  {
    path: '/play',
    name: 'MemoryGame',
    component: () => import('@/views/MemoryGame.vue')
  },
  {
    path: '/spread',
    name: 'Spread',
    component: () => import('@/views/Spread.vue')
  },
  {
    path: '/pet',
    name: 'Pet',
    component: () => import('@/views/Pet.vue')
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('@/views/Contact.vue')
  },
  {
    path: '/changelog',
    name: 'Changelog',
    component: () => import('@/views/Changelog.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
