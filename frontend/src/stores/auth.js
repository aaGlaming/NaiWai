import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { apiRequest } from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const ready = ref(false)
  const isAuthenticated = computed(() => !!user.value)

  async function bootstrap() {
    loading.value = true
    try {
      const data = await apiRequest('/api/v1/auth/me')
      user.value = data.user
    } catch {
      user.value = null
    } finally {
      loading.value = false
      ready.value = true
    }
    return user.value
  }

  async function login(payload) {
    const data = await apiRequest('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(payload) })
    user.value = data.user
    return user.value
  }

  async function register(payload) {
    const data = await apiRequest('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(payload) })
    user.value = data.user
    return user.value
  }

  async function logout() {
    await apiRequest('/api/v1/auth/logout', { method: 'POST' })
    user.value = null
  }

  return { user, loading, ready, isAuthenticated, bootstrap, login, register, logout }
})
