<script setup>
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { ref, computed, onMounted } from 'vue'
import CardReveal from '@/components/CardReveal.vue'
import DesktopPet from '@/components/DesktopPet.vue'
import AchievementToast from '@/components/AchievementToast.vue'
import { usePageMeta } from '@/composables/usePageMeta'
import { hasSeen, markSeen } from '@/utils/storage'
import AuthPanel from '@/components/AuthPanel.vue'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const isMenuOpen = ref(false)
const showCardReveal = ref(!hasSeen('naiwa_card_reveal_seen'))
const showPet = ref(!showCardReveal.value)
const showAuth = ref(false)
const auth = useAuthStore()
const userData = useUserStore()

usePageMeta()

const issueDate = '09.2026'

const navPrimary = [
  { path: '/', label: 'Index' },
  { path: '/gallery', label: 'Archive' },
  { path: '/lucky', label: 'Studio' },
  { path: '/about', label: 'About' }
]

const indexSections = [
  {
    id: '01',
    title: 'Index',
    items: [{ path: '/', label: '封面' }]
  },
  {
    id: '02',
    title: 'Archive',
    items: [
      { path: '/gallery', label: '图片库' },
      { path: '/collection', label: '图鉴收藏' }
    ]
  },
  {
    id: '03',
    title: 'Studio',
    items: [
      { path: '/lucky', label: '抽卡' },
      { path: '/meme', label: '梗图' },
      { path: '/wallpaper', label: '壁纸' },
      { path: '/tarot', label: '塔罗' },
      { path: '/quiz', label: '心情测试' },
      { path: '/play', label: '对对碰' },
      { path: '/spread', label: '漫游' }
    ]
  },
  {
    id: '04',
    title: 'About',
    items: [
      { path: '/about', label: '关于奶蛙' },
      { path: '/pet', label: '桌宠' },
      { path: '/changelog', label: '更新日志' },
      { path: '/contact', label: '来信' }
    ]
  }
]

function toggleMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function closeMenu() {
  isMenuOpen.value = false
}

function onCardRevealClose() {
  showCardReveal.value = false
  markSeen('naiwa_card_reveal_seen')
  showPet.value = true
}

const year = computed(() => new Date().getFullYear())

onMounted(async () => {
  const account = await auth.bootstrap()
  if (!account) return
  if (account.local_data_imported) {
    await userData.syncFromCloud()
    return
  }
  const localCount = userData.favorites.length + userData.collection.length
  if (!localCount || window.confirm(`检测到本机有 ${localCount} 条收藏/图鉴数据，是否合并到账号？`)) {
    try {
      await userData.importLocalData()
    } catch {
      await userData.syncFromCloud()
    }
  } else {
    await userData.syncFromCloud()
  }
})
</script>

<template>
  <div class="min-h-screen bg-paper text-ink">
    <header class="fixed top-0 left-0 right-0 z-50 bg-paper/95 border-b border-ink/15">
      <nav class="ed-page py-4 flex items-center justify-between gap-6">
        <RouterLink to="/" class="font-display text-xl tracking-tight text-ink no-underline">
          NAIWA
        </RouterLink>

        <div class="hidden md:flex items-center gap-8">
          <RouterLink
            v-for="item in navPrimary"
            :key="item.path"
            :to="item.path"
            class="ed-meta no-underline transition-colors duration-200"
            :class="route.path === item.path ? 'text-accent' : 'text-ink hover:text-accent'"
          >
            {{ item.label }}
          </RouterLink>
        </div>

        <div class="flex items-center gap-6">
          <span class="ed-meta hidden sm:inline">{{ issueDate }}</span>
          <RouterLink v-if="auth.isAuthenticated" to="/profile" class="ed-meta ed-link">
            {{ auth.user.nickname }}
          </RouterLink>
          <button v-else type="button" class="ed-meta text-ink hover:text-accent" @click="showAuth = true">
            登录
          </button>
          <button
            type="button"
            class="ed-meta text-ink hover:text-accent"
            :aria-expanded="isMenuOpen"
            aria-controls="site-index"
            @click="toggleMenu"
          >
            {{ isMenuOpen ? 'Close' : 'Menu' }}
          </button>
        </div>
      </nav>
    </header>

    <Teleport to="body">
      <div
        v-if="isMenuOpen"
        id="site-index"
        class="fixed inset-0 z-[80] bg-paper overflow-y-auto pt-24 pb-16"
      >
        <div class="ed-page">
          <p class="ed-meta mb-10">Issue 04 — Contents</p>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 md:gap-8">
            <div v-for="section in indexSections" :key="section.id">
              <p class="ed-num text-2xl mb-2">{{ section.id }}</p>
              <h2 class="font-display text-3xl mb-6">{{ section.title }}</h2>
              <ul class="space-y-3">
                <li v-for="item in section.items" :key="item.path">
                  <RouterLink
                    :to="item.path"
                    class="ed-link"
                    @click="closeMenu"
                  >
                    {{ item.label }}
                  </RouterLink>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <CardReveal v-if="showCardReveal" @close="onCardRevealClose" />
    <AuthPanel v-if="showAuth" @close="showAuth = false" />
    <AchievementToast />
    <DesktopPet v-if="showPet" />

    <main class="relative pt-20">
      <RouterView />
    </main>

    <footer class="mt-32 border-t border-ink/15">
      <div class="ed-page py-20 md:py-28">
        <p class="font-display text-4xl md:text-6xl leading-[0.95] mb-16 max-w-xl">
          Thank you<br />for reading.
        </p>
        <hr class="ed-rule mb-10" />
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-10">
          <div>
            <p class="ed-meta mb-2">Issue 04</p>
            <p class="ed-meta">{{ year }} · NAIWA</p>
          </div>
          <div class="flex flex-wrap gap-x-8 gap-y-3">
            <RouterLink to="/gallery" class="ed-link">Archive</RouterLink>
            <RouterLink to="/contact" class="ed-link">Contact</RouterLink>
            <RouterLink to="/changelog" class="ed-link">Log</RouterLink>
          </div>
        </div>
        <p class="ed-meta mt-16 max-w-lg">
          图片来源于公开传播的奶蛙素材，仅供个人娱乐。角色形象版权归原作者所有。
        </p>
      </div>
    </footer>
  </div>
</template>
