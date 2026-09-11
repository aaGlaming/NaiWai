<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import DrawCard from '@/components/DrawCard.vue'
import LegendaryEffect from '@/components/LegendaryEffect.vue'
import DrawHistory from '@/components/DrawHistory.vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { useUserStore } from '@/stores/user'
import { useImageStore } from '@/stores/images'
import { usePageMeta } from '@/composables/usePageMeta'

usePageMeta()
const user = useUserStore()
const imageStore = useImageStore()
const baseUrl = import.meta.env.BASE_URL || './'

const allImages = computed(() => imageStore.images)
const drawnCards = ref([])
const isDrawing = ref(false)
const showLegendary = ref(false)
const legendaryImage = ref(null)
const stats = ref({ N: 0, R: 0, SR: 0, SSR: 0 })
const drawMode = ref('single')

// 稀有度配置
const rarityConfig = {
  N: { label: 'Ordinary', color: '#8B877D', weight: 60 },
  R: { label: 'Noted', color: '#292825', weight: 25 },
  SR: { label: 'Selected', color: '#683E3D', weight: 12 },
  SSR: { label: 'Cover', color: '#A94B3C', weight: 3 }
}

function rollRarity() {
  let pity = user.stats.pityCount || 0
  if (pity >= 10) {
    user.setPity(0)
    return Math.random() < 0.2 ? 'SSR' : 'SR'
  }

  const totalWeight = Object.values(rarityConfig).reduce((sum, r) => sum + r.weight, 0)
  let random = Math.random() * totalWeight

  for (const [rarity, config] of Object.entries(rarityConfig)) {
    random -= config.weight
    if (random <= 0) {
      if (rarity === 'N' || rarity === 'R') user.setPity(pity + 1)
      else user.setPity(0)
      return rarity
    }
  }

  user.setPity(pity + 1)
  return 'N'
}

function getRandomImage() {
  const pool = allImages.value
  const index = Math.floor(Math.random() * pool.length)
  return pool[index]
}

async function drawCards(kind = 'draw') {
  if (isDrawing.value || allImages.value.length === 0) return
  if (kind === 'daily_draw' && !user.dailyDrawAvailable) return

  isDrawing.value = true
  drawnCards.value = []

  await new Promise(r => setTimeout(r, 100))

  const count = kind === 'daily_draw' ? 1 : (drawMode.value === 'single' ? 1 : 10)
  const cards = []
  let hasSSR = false

  for (let i = 0; i < count; i++) {
    const image = getRandomImage()
    const rarity = rollRarity()

    if (rarity === 'SSR') {
      hasSSR = true
      legendaryImage.value = image
    }

    cards.push({
      image,
      rarity,
      revealed: false
    })
  }

  drawnCards.value = cards

  if (count === 10 && !cards.some(c => c.rarity === 'SR' || c.rarity === 'SSR')) {
    const randomIndex = Math.floor(Math.random() * 10)
    drawnCards.value[randomIndex].rarity = 'SR'
  }

  if (hasSSR && legendaryImage.value) {
    setTimeout(() => {
      showLegendary.value = true
    }, 800)
  }

  user.track(kind, {
    count,
    ssr: cards.filter(c => c.rarity === 'SSR').length,
    pity: user.stats.pityCount || 0
  })
  isDrawing.value = false
}

// 翻转单张卡牌
function revealCard(index) {
  if (drawnCards.value[index] && !drawnCards.value[index].revealed) {
    drawnCards.value[index].revealed = true
    const rarity = drawnCards.value[index].rarity
    stats.value[rarity]++
    saveHistory(drawnCards.value[index])
  }
}

// 翻转所有卡牌
function revealAll() {
  drawnCards.value.forEach((card, index) => {
    if (!card.revealed) {
      setTimeout(() => {
        card.revealed = true
        stats.value[card.rarity]++
        saveHistory(card)
      }, index * 100)
    }
  })
}

// Enter键处理
function handleKeydown(e) {
  if (e.key === 'Enter' && drawnCards.value.length > 0 && !isDrawing.value) {
    const hasUnrevealed = drawnCards.value.some(c => !c.revealed)
    if (hasUnrevealed) {
      revealAll()
    }
  }
}

// 传说动画完成
function onLegendaryComplete() {
  showLegendary.value = false
}

// 跳过传说动画
function skipLegendary() {
  showLegendary.value = false
}

// 下载图片
function downloadImage(image) {
  const link = document.createElement('a')
  link.href = `${baseUrl}images/${image.filename}`
  link.download = image.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 保存抽卡记录
function saveHistory(card) {
  try {
    user.addToCollection(card.image.filename)
    const history = JSON.parse(localStorage.getItem('naiwa_draw_history') || '[]')
    history.push({
      image: card.image.filename,
      rarity: card.rarity,
      timestamp: Date.now()
    })
    if (history.length > 50) {
      history.splice(0, history.length - 50)
    }
    localStorage.setItem('naiwa_draw_history', JSON.stringify(history))
  } catch (e) {
    console.error('Failed to save history:', e)
  }
}

// 计算属性
const hasUnrevealed = computed(() => drawnCards.value.some(c => !c.revealed))

onMounted(() => {
  imageStore.fetchImages()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div>
    <LegendaryEffect
      v-if="showLegendary"
      @skip="skipLegendary"
      @complete="onLegendaryComplete"
    />

    <section class="ed-page pt-16 md:pt-24 pb-10">
      <p class="ed-meta mb-4">Studio — Insert</p>
      <h1 class="ed-display">抽卡.</h1>
      <p class="mt-6 text-charcoal max-w-md">单张或十连。稀有度写在字重里，不写在霓虹里。</p>
    </section>

    <section class="ed-page pb-24">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="lg:col-span-4 space-y-8">
          <div class="flex gap-8 border-b border-ink/15">
            <button
              type="button"
              class="ed-meta pb-3 border-b-2 -mb-px"
              :class="drawMode === 'single' ? 'text-accent border-accent' : 'border-transparent'"
              @click="drawMode = 'single'"
            >单抽</button>
            <button
              type="button"
              class="ed-meta pb-3 border-b-2 -mb-px"
              :class="drawMode === 'ten' ? 'text-accent border-accent' : 'border-transparent'"
              @click="drawMode = 'ten'"
            >十连</button>
          </div>

          <MaximalButton
            :loading="isDrawing"
            :disabled="isDrawing || !allImages.length"
            class="w-full"
            @click="drawCards('draw')"
          >
            {{ isDrawing ? '抽取中…' : drawMode === 'single' ? '抽一张' : '抽十张' }}
          </MaximalButton>

          <MaximalButton
            v-if="user.dailyDrawAvailable"
            variant="ghost"
            class="w-full"
            :disabled="isDrawing || !allImages.length"
            @click="drawCards('daily_draw')"
          >
            领取今日赠抽
          </MaximalButton>

          <p class="ed-meta">保底进度 {{ user.stats.pityCount || 0 }} / 10</p>

          <MaximalButton
            v-if="hasUnrevealed"
            variant="ghost"
            class="w-full"
            @click="revealAll"
          >
            全部翻开
          </MaximalButton>

          <p v-if="drawnCards.length > 0 && hasUnrevealed" class="ed-meta">
            Enter 一键翻开 · 点击逐张
          </p>

          <div class="border-t border-ink/15 pt-6">
            <h3 class="ed-meta mb-4">Odds</h3>
            <div v-for="(config, rarity) in rarityConfig" :key="rarity" class="flex justify-between py-2 text-sm">
              <span :style="{ color: config.color }">{{ config.label }} · {{ rarity }}</span>
              <span class="text-warm-gray">{{ config.weight }}%</span>
            </div>
          </div>

          <div class="border-t border-ink/15 pt-6">
            <h3 class="ed-meta mb-4">Tally</h3>
            <div class="flex justify-between py-1 text-sm"><span>合计</span><span>{{ stats.N + stats.R + stats.SR + stats.SSR }}</span></div>
            <div v-for="(config, rarity) in rarityConfig" :key="rarity" class="flex justify-between py-1 text-sm">
              <span>{{ config.label }}</span>
              <span>{{ stats[rarity] }}</span>
            </div>
          </div>

          <DrawHistory />
        </div>

        <div class="lg:col-span-8 min-h-[400px] border-t border-ink/15 pt-8 flex items-center justify-center">
          <div v-if="drawnCards.length === 0" class="text-center">
            <p class="font-display text-3xl mb-2">尚未开印。</p>
            <p class="ed-meta">选择单抽或十连</p>
          </div>
          <div v-else class="flex flex-wrap items-center justify-center gap-5">
            <DrawCard
              v-for="(card, index) in drawnCards"
              :key="index"
              :image="card.image"
              :rarity="card.rarity"
              :revealed="card.revealed"
              :index="index"
              :falling="true"
              @reveal="revealCard(index)"
              @download="downloadImage(card.image)"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
