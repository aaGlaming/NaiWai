<script setup>
import { computed, onMounted } from 'vue'
import { useImageStore } from '@/stores/images'
import { useUserStore } from '@/stores/user'
import { getDailyQuote, getDailyImageIndex } from '@/data/quotes'
import FavoriteButton from '@/components/FavoriteButton.vue'
import { RouterLink } from 'vue-router'

const store = useImageStore()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'
const quote = getDailyQuote()

const dailyImage = computed(() => {
  if (!store.images.length) return null
  const idx = getDailyImageIndex(store.images.length)
  return store.images[idx]
})

function checkIn() {
  user.track('checkin')
}

onMounted(() => store.fetchImages())
</script>

<template>
  <section class="ed-page py-20 md:py-28">
    <p class="ed-meta mb-4"><span class="ed-num">02</span> Daily plate</p>
    <hr class="ed-rule mb-10" />
    <div class="grid grid-cols-1 md:grid-cols-12 gap-10 items-start">
      <div class="md:col-span-7">
        <blockquote class="font-display text-3xl md:text-5xl leading-tight italic">
          “{{ quote }}”
        </blockquote>
        <p class="ed-meta mt-6">Words of the day</p>
        <div class="mt-8 flex flex-wrap items-center gap-6">
          <button
            type="button"
            class="ed-link"
            :disabled="user.checkedInToday"
            @click="checkIn"
          >
            {{ user.checkedInToday ? '今日已签' : '今日签到' }}
          </button>
          <span class="ed-meta">Streak {{ user.stats.streak || 0 }}</span>
          <RouterLink v-if="user.dailyDrawAvailable" to="/lucky" class="ed-link">领取今日赠抽</RouterLink>
          <RouterLink v-if="user.dailyDrawAvailable" to="/lucky" class="ed-link">领取今日赠抽</RouterLink>
        </div>
      </div>
      <div v-if="dailyImage" class="md:col-span-5 md:col-start-8">
        <div class="ed-img aspect-[4/5] relative">
          <img
            :src="`${baseUrl}images/${dailyImage.filename}`"
            :alt="dailyImage.filename"
            class="object-contain bg-warm-white"
          />
          <div class="absolute top-3 right-3">
            <FavoriteButton :filename="dailyImage.filename" size="sm" />
          </div>
        </div>
        <p class="ed-meta mt-3">{{ dailyImage.filename }}</p>
        <div class="mt-6 flex gap-8">
          <RouterLink to="/gallery" class="ed-link">浏览图库</RouterLink>
          <RouterLink to="/meme" class="ed-link">制作梗图</RouterLink>
        </div>
      </div>
      <p v-else class="ed-meta md:col-span-5">加载今日影像…</p>
    </div>
  </section>
</template>
