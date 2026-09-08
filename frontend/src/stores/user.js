import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { loadJson, saveJson } from '@/utils/storage'
import { ACHIEVEMENTS, checkAchievement } from '@/data/achievements'
import { apiRequest } from '@/utils/api'
import { useAuthStore } from '@/stores/auth'

const STORAGE_KEY = 'naiwa_user_v1'

const DEFAULT_STATS = {
  draws: 0,
  ssrCount: 0,
  wallpapers: 0,
  tarot: 0,
  quiz: 0,
  memes: 0,
  downloads: 0,
  matches: 0,
  streak: 0,
  lastCheckin: ''
}

function todayKey() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function yesterdayKey() {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export { todayKey }

export const useUserStore = defineStore('user', () => {
  const saved = loadJson(STORAGE_KEY, {})
  const favorites = ref(saved.favorites || [])
  const collection = ref(saved.collection || [])
  const unlocked = ref(saved.unlocked || [])
  const stats = ref({ ...DEFAULT_STATS, ...(saved.stats || {}) })
  const pendingToast = ref(null)
  const syncing = ref(false)
  const syncError = ref(null)

  function persist() {
    saveJson(STORAGE_KEY, {
      favorites: favorites.value,
      collection: collection.value,
      unlocked: unlocked.value,
      stats: stats.value
    })
  }

  function evaluateAchievements() {
    const state = {
      favorites: favorites.value,
      collection: collection.value,
      stats: stats.value
    }
    for (const ach of ACHIEVEMENTS) {
      if (!unlocked.value.includes(ach.id) && checkAchievement(ach.id, state)) {
        unlocked.value.push(ach.id)
        pendingToast.value = ach
      }
    }
    persist()
  }

  function clearToast() {
    pendingToast.value = null
  }

  async function toggleFavorite(filename) {
    const i = favorites.value.indexOf(filename)
    const adding = i < 0
    if (adding) favorites.value.push(filename)
    else favorites.value.splice(i, 1)
    persist()
    evaluateAchievements()
    if (useAuthStore().isAuthenticated) {
      try {
        await apiRequest(`/api/v1/me/favorites/${encodeURIComponent(filename)}`, {
          method: adding ? 'PUT' : 'DELETE'
        })
      } catch (error) {
        if (adding) favorites.value = favorites.value.filter(item => item !== filename)
        else favorites.value.push(filename)
        persist()
        syncError.value = error.message
      }
    }
  }

  function isFavorite(filename) {
    return favorites.value.includes(filename)
  }

  async function addToCollection(filename) {
    if (!collection.value.includes(filename)) {
      collection.value.push(filename)
      persist()
      evaluateAchievements()
    }
    if (useAuthStore().isAuthenticated) {
      try {
        await apiRequest(`/api/v1/me/collection/${encodeURIComponent(filename)}`, { method: 'PUT' })
      } catch (error) {
        syncError.value = error.message
      }
    }
  }

  const checkedInToday = computed(() => stats.value.lastCheckin === todayKey())

  function track(event, payload = {}) {
    switch (event) {
      case 'draw':
        stats.value.draws += payload.count || 1
        if (payload.ssr) stats.value.ssrCount += payload.ssr
        break
      case 'wallpaper':
        stats.value.wallpapers += 1
        break
      case 'tarot':
        stats.value.tarot += 1
        break
      case 'quiz':
        stats.value.quiz += 1
        break
      case 'meme':
        stats.value.memes += 1
        break
      case 'download':
        stats.value.downloads += 1
        break
      case 'match':
        stats.value.matches = (stats.value.matches || 0) + 1
        break
      case 'checkin': {
        const today = todayKey()
        if (stats.value.lastCheckin === today) return
        if (stats.value.lastCheckin === yesterdayKey()) {
          stats.value.streak = (stats.value.streak || 0) + 1
        } else {
          stats.value.streak = 1
        }
        stats.value.lastCheckin = today
        break
      }
      default:
        break
    }
    persist()
    evaluateAchievements()
    if (useAuthStore().isAuthenticated && event !== 'checkin') {
      apiRequest('/api/v1/me/events', {
        method: 'POST',
        body: JSON.stringify({ event, count: payload.count || 1, ssr: payload.ssr || 0 })
      }).then(result => applyRemoteData(result.data)).catch(error => { syncError.value = error.message })
    }
  }

  function applyRemoteData(data) {
    favorites.value = data.favorites || []
    collection.value = data.collection || []
    unlocked.value = data.unlocked || []
    stats.value = { ...DEFAULT_STATS, ...(data.stats || {}) }
    persist()
  }

  async function syncFromCloud() {
    if (!useAuthStore().isAuthenticated) return false
    syncing.value = true
    syncError.value = null
    try {
      const data = await apiRequest('/api/v1/me/data')
      applyRemoteData(data)
      return true
    } catch (error) {
      syncError.value = error.message
      return false
    } finally {
      syncing.value = false
    }
  }

  async function importLocalData() {
    const payload = {
      favorites: [...favorites.value],
      collection: [...collection.value],
      unlocked: [...unlocked.value],
      stats: { ...stats.value }
    }
    const result = await apiRequest('/api/v1/me/import-local-data', {
      method: 'POST', body: JSON.stringify(payload)
    })
    applyRemoteData(result.data)
  }

  function clearLocalData() {
    favorites.value = []
    collection.value = []
    unlocked.value = []
    stats.value = { ...DEFAULT_STATS }
    persist()
  }

  const achievementProgress = computed(() =>
    ACHIEVEMENTS.map(a => ({
      ...a,
      unlocked: unlocked.value.includes(a.id)
    }))
  )

  return {
    favorites,
    collection,
    unlocked,
    stats,
    pendingToast,
    syncing,
    syncError,
    achievementProgress,
    checkedInToday,
    toggleFavorite,
    isFavorite,
    addToCollection,
    track,
    evaluateAchievements,
    clearToast,
    syncFromCloud,
    importLocalData,
    clearLocalData
  }
})
