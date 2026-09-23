<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useImageStore } from '@/stores/images'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'
import MaximalButton from '@/components/ui/MaximalButton.vue'

usePageMeta()

const BEST_KEY = 'naiwa_match_best'
const COLS = 4
const PAIR_COUNT = 8

const store = useImageStore()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'

const cards = ref([])
const lock = ref(false)
const openIds = ref([])
const moves = ref(0)
const elapsed = ref(0)
const started = ref(false)
const finished = ref(false)
const focusIndex = ref(0)
const boardRef = ref(null)
const reduceMotion = ref(false)
let timer = null

const best = ref(Number(localStorage.getItem(BEST_KEY) || 0))

const matchedCount = computed(() => cards.value.filter(c => c.matched).length / 2)
const timeLabel = computed(() => formatTime(elapsed.value))
const bestLabel = computed(() => (best.value ? formatTime(best.value) : '—'))

function formatTime(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, '0')
  const s = String(sec % 60).padStart(2, '0')
  return `${m}:${s}`
}

function shuffle(list) {
  const a = [...list]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function deal() {
  stopTimer()
  const pool = store.images.filter(img => img.filename)
  if (pool.length < PAIR_COUNT) return
  const picks = shuffle(pool).slice(0, PAIR_COUNT)
  const deck = shuffle(
    picks.flatMap((img, i) => [
      { uid: `${i}-a`, filename: img.filename, flipped: false, matched: false },
      { uid: `${i}-b`, filename: img.filename, flipped: false, matched: false }
    ])
  )
  cards.value = deck
  openIds.value = []
  lock.value = false
  moves.value = 0
  elapsed.value = 0
  started.value = false
  finished.value = false
  focusIndex.value = 0
}

function startTimer() {
  if (started.value) return
  started.value = true
  timer = setInterval(() => { elapsed.value += 1 }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function faceUp(card) {
  return card.flipped || card.matched
}

function flipAt(index) {
  if (lock.value || finished.value) return
  const card = cards.value[index]
  if (!card || card.matched || card.flipped) return

  startTimer()
  card.flipped = true
  openIds.value.push(index)

  if (openIds.value.length < 2) return

  moves.value += 1
  const [a, b] = openIds.value
  const ca = cards.value[a]
  const cb = cards.value[b]

  if (ca.filename === cb.filename) {
    ca.matched = true
    cb.matched = true
    user.addToCollection(ca.filename)
    openIds.value = []
    if (cards.value.every(c => c.matched)) onWin()
  } else {
    lock.value = true
    const delay = reduceMotion.value ? 200 : 700
    setTimeout(() => {
      ca.flipped = false
      cb.flipped = false
      openIds.value = []
      lock.value = false
    }, delay)
  }
}

function onWin() {
  stopTimer()
  finished.value = true
  user.track('match')
  if (!best.value || elapsed.value < best.value) {
    best.value = elapsed.value
    localStorage.setItem(BEST_KEY, String(elapsed.value))
  }
}

function focusCard(index) {
  focusIndex.value = index
  boardRef.value?.querySelectorAll('button')[index]?.focus()
}

function onKey(e) {
  if (!cards.value.length || !boardRef.value?.contains(e.target)) return
  const buttons = [...boardRef.value.querySelectorAll('button')]
  const current = buttons.indexOf(e.target)
  if (current >= 0) focusIndex.value = current
  const cols = COLS
  const max = cards.value.length - 1
  if (e.key === 'ArrowRight') {
    e.preventDefault()
    focusCard(Math.min(max, focusIndex.value + 1))
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault()
    focusCard(Math.max(0, focusIndex.value - 1))
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusCard(Math.min(max, focusIndex.value + cols))
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusCard(Math.max(0, focusIndex.value - cols))
  }
}

watch(() => store.images.length, (n) => {
  if (n && !cards.value.length) deal()
})

onMounted(async () => {
  reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  await store.fetchImages()
  if (store.images.length) deal()
})

onUnmounted(() => {
  stopTimer()
})
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-8">
      <p class="ed-meta mb-4"><span class="ed-num">08</span> Game</p>
      <h1 class="ed-display">
        Match the<br /><em class="italic">ordinary.</em>
      </h1>
      <p class="mt-6 text-charcoal max-w-md">翻开两张。同一只肚子，就算对上了。</p>
    </section>

    <section class="ed-page pb-6">
      <div class="flex flex-wrap gap-x-10 gap-y-2 ed-meta border-y border-ink/15 py-4">
        <span>Moves {{ moves }}</span>
        <span>Time {{ timeLabel }}</span>
        <span>Best {{ bestLabel }}</span>
        <span>Pairs {{ matchedCount }} / {{ PAIR_COUNT }}</span>
      </div>
    </section>

    <section class="ed-page pb-24">
      <p v-if="store.loading" class="ed-meta py-16">Loading plates…</p>
      <p v-else-if="store.error" class="text-accent py-16">{{ store.error }}</p>
      <div v-else ref="boardRef" class="grid grid-cols-4 gap-2 md:gap-4 max-w-3xl" @keydown="onKey">
        <button
          v-for="(card, index) in cards"
          :key="card.uid"
          type="button"
          class="match-card aspect-[3/4] bg-warm-white border border-ink/15 p-0 relative"
          :class="{ 'ring-1 ring-accent': focusIndex === index }"
          :aria-label="faceUp(card) ? card.filename : `牌 ${index + 1}`"
          :aria-pressed="faceUp(card)"
          @click="focusIndex = index; flipAt(index)"
        >
          <div class="match-inner" :class="{ flipped: faceUp(card), flat: reduceMotion }">
            <div class="match-face match-back flex items-center justify-center">
              <span class="ed-num text-xl">{{ String(index + 1).padStart(2, '0') }}</span>
            </div>
            <div class="match-face match-front">
              <img
                :src="`${baseUrl}images/${card.filename}`"
                :alt="card.filename"
                class="w-full h-full object-contain bg-paper"
                draggable="false"
              />
            </div>
          </div>
        </button>
      </div>

      <div v-if="finished" class="mt-12 max-w-md">
        <p class="ed-meta mb-2">Complete</p>
        <p class="font-display text-3xl mb-6">{{ moves }} 步 · {{ timeLabel }}</p>
        <MaximalButton @click="deal">再来一局</MaximalButton>
      </div>
      <div v-else class="mt-10">
        <MaximalButton variant="ghost" @click="deal">重洗</MaximalButton>
      </div>
      <p class="ed-meta mt-8">在牌面上用方向键移动，Enter 或空格翻开</p>
    </section>
  </div>
</template>

<style scoped>
.match-card {
  perspective: 800px;
}
.match-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 350ms ease;
}
.match-inner.flipped {
  transform: rotateY(180deg);
}
.match-inner.flat {
  transition: none;
  transform: none;
}
.match-inner.flat .match-front {
  opacity: 0;
}
.match-inner.flat.flipped .match-front {
  opacity: 1;
}
.match-inner.flat.flipped .match-back {
  opacity: 0;
}
.match-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  overflow: hidden;
}
.match-back {
  background: #F8F6F0;
}
.match-front {
  transform: rotateY(180deg);
  background: #F8F6F0;
}
@media (prefers-reduced-motion: reduce) {
  .match-inner:not(.flat) {
    transition: none;
  }
}
</style>
