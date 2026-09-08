<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'

usePageMeta()
const auth = useAuthStore()
const data = useUserStore()
const router = useRouter()
const desktopReady = ref(false)
const desktopMessage = ref('')
const completion = computed(() => Math.round((data.collection.length / 447) * 100))
const metrics = computed(() => [
  ['收藏', data.favorites.length], ['图鉴', data.collection.length], ['抽卡', data.stats.draws],
  ['SSR', data.stats.ssrCount], ['下载', data.stats.downloads], ['成就', data.unlocked.length]
])

onMounted(() => {
  if (auth.isAuthenticated) data.syncFromCloud()
  const markDesktopReady = () => { desktopReady.value = !!window.pywebview?.api }
  markDesktopReady()
  window.addEventListener('pywebviewready', markDesktopReady, { once: true })
})

async function logout() {
  await auth.logout()
  data.clearLocalData()
  router.push('/')
}

async function desktopAction(action) {
  desktopMessage.value = ''
  try {
    const result = await window.pywebview.api[action]()
    if (result.cancelled) return
    if (!result.success) throw new Error(result.error || '操作失败')
    if (action === 'backup_data') desktopMessage.value = `备份完成：${result.path}`
    if (action === 'open_data_folder') desktopMessage.value = '已打开数据目录'
    if (action === 'restore_data') {
      desktopMessage.value = '恢复完成，正在重新载入…'
      window.location.href = '/api/v1/auth/desktop-login'
    }
  } catch (error) {
    desktopMessage.value = error.message || '操作失败'
  }
}
</script>

<template>
  <div class="ed-page pt-16 md:pt-24 pb-24">
    <template v-if="auth.isAuthenticated">
      <p class="ed-meta mb-5">Personal account</p>
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-8 border-b border-ink/15 pb-10">
        <div>
          <h1 class="ed-display">{{ auth.user.nickname }}.</h1>
          <p class="text-charcoal mt-4">@{{ auth.user.username }} · 图鉴完成度 {{ completion }}%</p>
        </div>
        <button v-if="!desktopReady" type="button" class="ed-link" @click="logout">退出登录</button>
      </div>
      <section class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-px bg-ink/15 border border-ink/15 mt-12">
        <div v-for="metric in metrics" :key="metric[0]" class="bg-paper p-5">
          <p class="ed-meta mb-4">{{ metric[0] }}</p>
          <p class="ed-num text-4xl">{{ metric[1] }}</p>
        </div>
      </section>
      <section class="grid md:grid-cols-2 gap-12 mt-16">
        <div>
          <p class="ed-meta mb-6"><span class="ed-num">01</span> Cloud archive</p>
          <h2 class="font-display text-3xl mb-3">数据已同步</h2>
          <p class="text-charcoal">收藏、抽卡图鉴、统计与成就会保存到 MySQL，可在其他设备登录后恢复。</p>
          <RouterLink to="/collection" class="ed-link inline-block mt-6">打开图鉴 →</RouterLink>
        </div>
        <div>
          <p class="ed-meta mb-6"><span class="ed-num">02</span> Achievements</p>
          <div v-for="ach in data.achievementProgress.slice(0, 5)" :key="ach.id" class="py-3 border-b border-ink/10 flex justify-between">
            <span>{{ ach.title }}</span><span>{{ ach.unlocked ? '●' : '○' }}</span>
          </div>
        </div>
      </section>
      <section v-if="desktopReady" class="mt-16 border-t border-ink/15 pt-10">
        <p class="ed-meta mb-6"><span class="ed-num">03</span> Local data</p>
        <h2 class="font-display text-3xl mb-3">本地数据管理</h2>
        <p class="text-charcoal mb-7">数据保存在此电脑，可随时备份、恢复或打开数据目录。</p>
        <div class="flex flex-wrap gap-5">
          <button type="button" class="ed-link" @click="desktopAction('backup_data')">导出备份</button>
          <button type="button" class="ed-link" @click="desktopAction('restore_data')">恢复备份</button>
          <button type="button" class="ed-link" @click="desktopAction('open_data_folder')">打开数据目录</button>
        </div>
        <p v-if="desktopMessage" class="text-sm text-charcoal mt-6 break-all">{{ desktopMessage }}</p>
      </section>
    </template>
    <template v-else>
      <p class="ed-meta mb-5">Personal account</p>
      <h1 class="ed-display">尚未登录.</h1>
      <p class="text-charcoal mt-6">请从顶部导航打开登录窗口。</p>
    </template>
  </div>
</template>
