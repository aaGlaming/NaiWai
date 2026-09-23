<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useImageStore } from '@/stores/images'
import { usePageMeta } from '@/composables/usePageMeta'
import FavoriteButton from '@/components/FavoriteButton.vue'

usePageMeta()

const route = useRoute()
const router = useRouter()
const store = useImageStore()
const baseUrl = import.meta.env.BASE_URL || './'

const index = ref(0)

const total = computed(() => store.images.length)
const current = computed(() => store.images[index.value] || null)
const numLabel = computed(() => {
  if (!total.value) return '—'
  return `${String(index.value + 1).padStart(3, '0')} / ${String(total.value).padStart(3, '0')}`
})

function syncFromQuery() {
  const f = route.query.f
  if (typeof f === 'string' && store.images.length) {
    const i = store.images.findIndex(img => img.filename === f)
    if (i >= 0) index.value = i
  }
}

function go(delta) {
  if (!total.value) return
  index.value = (index.value + delta + total.value) % total.value
  router.replace({ path: '/spread', query: { f: store.images[index.value].filename } })
}

function onKey(e) {
  if (e.target.closest('a, button, input, textarea, select')) return
  if (e.key === 'ArrowLeft') {
    e.preventDefault()
    go(-1)
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    go(1)
  }
}

watch(() => store.images.length, () => syncFromQuery())
watch(() => route.query.f, () => syncFromQuery())

onMounted(async () => {
  await store.fetchImages()
  syncFromQuery()
  window.addEventListener('keydown', onKey)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div>
    <section class="ed-page pt-12 md:pt-16 pb-6 flex items-end justify-between gap-6">
      <div>
        <p class="ed-meta mb-2">Spread</p>
        <h1 class="font-display text-4xl md:text-5xl">漫游.</h1>
      </div>
      <p class="ed-meta">{{ numLabel }}</p>
    </section>

    <section class="ed-page pb-8">
      <p v-if="store.loading" class="ed-meta py-24">Loading…</p>
      <div v-else-if="store.error" class="py-24">
        <p class="text-accent mb-4">{{ store.error }}</p>
        <button type="button" class="ed-link" @click="store.fetchImages()">重试</button>
      </div>
      <p v-else-if="!current" class="ed-meta py-24">还没有可漫游的影像。</p>
      <div v-else class="bg-warm-white min-h-[40dvh] md:min-h-[70vh] flex items-center justify-center">
        <img
          :src="`${baseUrl}images/${current.filename}`"
          :alt="current.filename"
          class="max-w-full max-h-[58dvh] md:max-h-[78vh] object-contain"
        />
      </div>
    </section>

    <section v-if="current" class="ed-page pb-24">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 border-t border-ink/15 pt-6">
        <div>
          <p class="ed-meta">Plate</p>
          <p class="font-display text-xl mt-1 break-all">{{ current.filename }}</p>
        </div>
        <div class="flex flex-wrap items-center gap-6">
          <FavoriteButton :filename="current.filename" size="md" />
          <button type="button" class="ed-link" @click="go(-1)">上一张</button>
          <button type="button" class="ed-link" @click="go(1)">下一张</button>
        </div>
      </div>
      <p class="ed-meta mt-6">← → 翻页</p>
    </section>
  </div>
</template>
