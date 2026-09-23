<script setup>
import { ref } from 'vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { usePageMeta } from '@/composables/usePageMeta'
import { loadJson, saveJson } from '@/utils/storage'
import { apiRequest } from '@/utils/api'

usePageMeta()

const form = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const submitted = ref(false)
const submitting = ref(false)
const error = ref(null)

async function handleSubmit() {
  error.value = null
  const name = form.value.name.trim()
  const email = form.value.email.trim()
  const subject = form.value.subject.trim()
  const message = form.value.message.trim()
  if (!name || !email || !subject || message.length < 2) {
    error.value = '请填写姓名、邮箱和主题，正文至少写 2 个字。'
    return
  }
  form.value = { name, email, subject, message }
  submitting.value = true
  const payload = { name, email, subject, message, time: new Date().toISOString() }

  try {
    await apiRequest('/api/contact', {
      method: 'POST',
      body: JSON.stringify(form.value)
    })
    submitted.value = true
    form.value = { name: '', email: '', subject: '', message: '' }
    submitting.value = false
    return
  } catch (_) { /* fallback */ }

  const inbox = loadJson('naiwa_contact_messages', [])
  inbox.push(payload)
  saveJson('naiwa_contact_messages', inbox)

  const mailSubject = encodeURIComponent(`[奶蛙世界] ${subject}`)
  const mailBody = encodeURIComponent(
    `姓名：${name}\n邮箱：${email}\n\n${message}`
  )
  window.location.href = `mailto:a36194113019@gmail.com?subject=${mailSubject}&body=${mailBody}`

  submitted.value = true
  form.value = { name: '', email: '', subject: '', message: '' }
  submitting.value = false
}

const contactMethods = [
  { title: '邮箱', value: 'a36194113019@gmail.com' },
  { title: '社交媒体', value: '13056991779' },
  { title: 'GitHub', value: 'github.com/aaGlaming' }
]

const faqItems = [
  {
    question: '奶蛙图片可以商用吗？',
    answer: '不可以。版权归原作者所有，本站图片仅供个人娱乐。'
  },
  {
    question: '如何下载图片？',
    answer: '在图片库中打开大图，使用 Save，或右键另存为。'
  },
  {
    question: '图片会定期更新吗？',
    answer: '会不定期增补热门表情与创作。'
  },
  {
    question: '我可以提交自己的创作吗？',
    answer: '欢迎。通过本页表单或邮箱提交即可。'
  }
]
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-12">
      <p class="ed-meta mb-6">Submissions — Letters</p>
      <h1 class="ed-display">
        来信<br /><em class="italic">与页边。</em>
      </h1>
    </section>

    <section class="ed-page py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 border-t border-ink/15 pt-8">
        <div v-for="m in contactMethods" :key="m.title">
          <p class="ed-meta mb-2">{{ m.title }}</p>
          <p class="font-display text-xl">{{ m.value }}</p>
        </div>
      </div>
    </section>

    <section class="ed-page py-16 max-w-2xl">
      <p class="ed-meta mb-8"><span class="ed-num">01</span> Write to us</p>
      <div v-if="submitted">
        <p class="font-display text-3xl mb-4">已收到。</p>
        <p class="text-charcoal mb-8">感谢来信，我们会尽快回复。</p>
        <MaximalButton variant="ghost" @click="submitted = false">再写一封</MaximalButton>
      </div>
      <form v-else class="space-y-8" @submit.prevent="handleSubmit">
        <p class="text-charcoal text-sm">姓名、邮箱、主题和正文都需要填写。</p>
        <p v-if="error" class="text-accent text-sm" role="alert">{{ error }}</p>
        <label class="block">
          <span class="ed-meta">姓名</span>
          <input v-model="form.name" type="text" required autocomplete="name" class="ed-input" :aria-invalid="error ? 'true' : undefined" />
        </label>
        <label class="block">
          <span class="ed-meta">邮箱</span>
          <input v-model="form.email" type="email" required autocomplete="email" class="ed-input" :aria-invalid="error ? 'true' : undefined" />
        </label>
        <label class="block">
          <span class="ed-meta">主题</span>
          <input v-model="form.subject" type="text" required class="ed-input" :aria-invalid="error ? 'true' : undefined" />
        </label>
        <label class="block">
          <span class="ed-meta">正文</span>
          <textarea v-model="form.message" required class="ed-input" :aria-invalid="error ? 'true' : undefined"></textarea>
        </label>
        <MaximalButton :loading="submitting" :disabled="submitting">
          {{ submitting ? '发送中…' : '投递' }}
        </MaximalButton>
      </form>
    </section>

    <section class="ed-page py-16 pb-24">
      <p class="ed-meta mb-4"><span class="ed-num">02</span> FAQ</p>
      <hr class="ed-rule mb-2" />
      <article v-for="item in faqItems" :key="item.question" class="py-8 border-b border-ink/10">
        <h3 class="font-display text-2xl mb-3">{{ item.question }}</h3>
        <p class="text-charcoal">{{ item.answer }}</p>
      </article>
    </section>
  </div>
</template>
