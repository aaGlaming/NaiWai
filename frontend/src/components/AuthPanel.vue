<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import MaximalButton from '@/components/ui/MaximalButton.vue'

const emit = defineEmits(['close', 'authenticated'])
const auth = useAuthStore()
const userData = useUserStore()
const mode = ref('login')
const submitting = ref(false)
const error = ref('')
const mergeLocal = ref(true)
const form = ref({ username: '', password: '', nickname: '', email: '' })
const localCount = computed(() => userData.favorites.length + userData.collection.length)

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.email) delete payload.email
    const account = mode.value === 'login' ? await auth.login(payload) : await auth.register(payload)
    if (!account.local_data_imported && mergeLocal.value) await userData.importLocalData()
    else await userData.syncFromCloud()
    emit('authenticated')
    emit('close')
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-[100] bg-ink/40 flex items-center justify-center p-4" @click.self="emit('close')">
    <section class="bg-paper border border-ink/20 w-full max-w-md p-7 md:p-10 shadow-2xl">
      <div class="flex justify-between items-start mb-8">
        <div>
          <p class="ed-meta mb-2">Naiwa account</p>
          <h2 class="font-display text-4xl">{{ mode === 'login' ? '欢迎回来。' : '加入奶蛙世界。' }}</h2>
        </div>
        <button type="button" class="ed-meta hover:text-accent" @click="emit('close')">Close</button>
      </div>
      <form class="space-y-5" @submit.prevent="submit">
        <p v-if="error" class="text-accent text-sm">{{ error }}</p>
        <label class="block">
          <span class="ed-meta">用户名{{ mode === 'login' ? ' / 邮箱' : '' }}</span>
          <input v-model.trim="form.username" class="ed-input" required minlength="3" maxlength="32" autocomplete="username" />
        </label>
        <label v-if="mode === 'register'" class="block">
          <span class="ed-meta">昵称</span>
          <input v-model.trim="form.nickname" class="ed-input" required maxlength="50" />
        </label>
        <label v-if="mode === 'register'" class="block">
          <span class="ed-meta">邮箱（可选）</span>
          <input v-model.trim="form.email" class="ed-input" type="email" autocomplete="email" />
        </label>
        <label class="block">
          <span class="ed-meta">密码</span>
          <input v-model="form.password" class="ed-input" type="password" required minlength="8" autocomplete="current-password" />
        </label>
        <label v-if="localCount && !auth.user?.local_data_imported" class="flex items-start gap-3 text-sm text-charcoal">
          <input v-model="mergeLocal" type="checkbox" class="mt-1" />
          <span>登录后合并本机的 {{ localCount }} 条收藏/图鉴数据</span>
        </label>
        <MaximalButton class="w-full" :loading="submitting" :disabled="submitting">
          {{ submitting ? '处理中…' : mode === 'login' ? '登录' : '注册并登录' }}
        </MaximalButton>
      </form>
      <button type="button" class="ed-link mt-7" @click="mode = mode === 'login' ? 'register' : 'login'; error = ''">
        {{ mode === 'login' ? '没有账号？立即注册' : '已有账号？返回登录' }}
      </button>
    </section>
  </div>
</template>
