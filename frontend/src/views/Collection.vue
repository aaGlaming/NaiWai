<script setup>
import { ref, computed, onMounted } from 'vue'
import { useImageStore } from '@/stores/images'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'
import FavoriteButton from '@/components/FavoriteButton.vue'
import { RouterLink } from 'vue-router'

usePageMeta()

const store = useImageStore()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'
const activeTab = ref('favorites')

const favoriteImages = computed(() =>
  user.favorites.map(f => store.getByFilename(f)).filter(Boolean)
)

const collectionImages = computed(() =>
  user.collection.map(f => store.getByFilename(f)).filter(Boolean)
)

const displayImages = computed(() =>
  activeTab.value === 'favorites' ? favoriteImages.value : collectionImages.value
)

onMounted(() => store.fetchImages())
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-10">
      <p class="ed-meta mb-4">Personal archive</p>
      <h1 class="ed-display">图鉴.</h1>
    </section>

    <section class="ed-page pb-8">
      <div class="flex flex-wrap gap-8 border-b border-ink/15">
        <button
          v-for="t in [
            { id: 'favorites', label: '收藏', count: user.favorites.length },
            { id: 'collection', label: '抽卡图鉴', count: user.collection.length },
            { id: 'achievements', label: '成就', count: user.unlocked.length }
          ]"
          :key="t.id"
          type="button"
          class="ed-meta pb-3 border-b-2 -mb-px"
          :aria-pressed="activeTab === t.id"
          :class="activeTab === t.id ? 'text-accent border-accent' : 'text-ink border-transparent'"
          @click="activeTab = t.id"
        >
          {{ t.label }} {{ String(t.count).padStart(2, '0') }}
        </button>
      </div>
    </section>

    <section v-if="activeTab !== 'achievements'" class="ed-page pb-24">
      <div v-if="displayImages.length === 0" class="py-20">
        <p class="ed-meta mb-4">
          {{ activeTab === 'favorites' ? '还没有收藏。' : '还没有解锁。' }}
        </p>
        <RouterLink :to="activeTab === 'favorites' ? '/gallery' : '/lucky'" class="ed-link">
          {{ activeTab === 'favorites' ? '去图片库' : '去抽卡' }}
        </RouterLink>
      </div>
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-x-4 gap-y-8">
        <article v-for="img in displayImages" :key="img.filename">
          <div class="ed-img aspect-square relative mb-2">
            <img :src="`${baseUrl}images/${img.filename}`" :alt="img.filename" class="object-contain bg-warm-white" />
            <div class="absolute top-2 right-2">
              <FavoriteButton :filename="img.filename" size="sm" />
            </div>
          </div>
          <p class="ed-meta truncate">{{ img.filename }}</p>
        </article>
      </div>
    </section>

    <section v-else class="ed-page pb-24">
      <p class="ed-meta mb-8"><span class="ed-num">03</span> Badges</p>
      <div
        v-for="ach in user.achievementProgress"
        :key="ach.id"
        class="grid grid-cols-12 gap-4 py-6 border-b border-ink/10"
      >
        <span class="col-span-2 ed-num">{{ ach.unlocked ? '●' : '○' }}<span class="sr-only">{{ ach.unlocked ? '已解锁' : '未解锁' }}</span></span>
        <div class="col-span-10">
          <p class="font-display text-2xl">{{ ach.title }}</p>
          <p class="text-sm text-warm-gray mt-1">{{ ach.desc }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
