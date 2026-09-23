<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useImageStore } from '@/stores/images'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { loadJson, saveJson, markSeen } from '@/utils/storage'
import {
  SHOP,
  createRun,
  fireHook,
  useDynamite,
  buyShopItem,
  leaveShop,
  tick,
  hookTip,
  hashSeed
} from '@/utils/miner'

usePageMeta()

const W = 720
const H = 500
const DAILY_KEY = 'naiwa_mine_daily_v1'

const store = useImageStore()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'

const canvasRef = ref(null)
const mode = ref('arcade')
const run = ref(null)
const reduceMotion = ref(false)
const imageCache = new Map()

const board = ref(loadJson(DAILY_KEY, { today: '', todayBest: 0, records: [] }))

const phase = computed(() => run.value?.phase || 'idle')
const playing = computed(() => run.value && !['shop', 'fail', 'daily_done'].includes(phase.value))

function todayKey() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function syncBoardDate() {
  const today = todayKey()
  if (board.value.today !== today) {
    board.value = { ...board.value, today, todayBest: 0 }
    saveJson(DAILY_KEY, board.value)
  }
}

function loadImage(filename) {
  if (imageCache.has(filename)) return imageCache.get(filename)
  const img = new Image()
  img.src = `${baseUrl}images/${filename}`
  imageCache.set(filename, img)
  return img
}

function freshSeed() {
  if (mode.value === 'daily') return hashSeed(`naiwa-mine-${todayKey()}`)
  return Math.floor(Math.random() * 2 ** 32) >>> 0
}

function startRun() {
  if (!store.images.length) return
  syncBoardDate()
  run.value = createRun({
    mode: mode.value,
    images: store.images,
    width: W,
    height: H,
    reduceMotion: reduceMotion.value,
    seed: freshSeed()
  })
}

function settleRun(current) {
  if (!current || current.tracked) return
  current.tracked = true
  if (current.mode === 'daily') {
    const today = todayKey()
    const records = [{ date: today, score: current.score, at: Date.now() }, ...(board.value.records || [])].slice(0, 10)
    const todayBest = Math.max(board.value.today === today ? board.value.todayBest : 0, current.score)
    board.value = { today, todayBest, records }
    saveJson(DAILY_KEY, board.value)
    user.track('daily_mine')
  } else {
    user.track('mine')
  }
}

function onShopBuy(id) {
  if (!run.value || run.value.phase !== 'shop') return
  if (!buyShopItem(run.value, id)) return
  markSeen('naiwa_mine_bought')
  user.evaluateAchievements()
}

function onLeaveShop() {
  if (!run.value) return
  leaveShop(run.value)
}

function tryFire() {
  if (!run.value || !playing.value) return
  fireHook(run.value)
}

function tryDynamite() {
  if (!run.value) return
  useDynamite(run.value)
}

function onKey(e) {
  if (e.key === ' ' || e.code === 'Space') {
    e.preventDefault()
    tryFire()
  } else if (e.key === 'd' || e.key === 'D') {
    e.preventDefault()
    tryDynamite()
  }
}

function draw(ctx, current) {
  ctx.clearRect(0, 0, W, H)
  ctx.fillStyle = '#F4F0E8'
  ctx.fillRect(0, 0, W, H)
  ctx.strokeStyle = 'rgba(41,40,37,0.12)'
  ctx.beginPath()
  ctx.moveTo(0, current.origin.y + 18)
  ctx.lineTo(W, current.origin.y + 18)
  ctx.stroke()

  ctx.fillStyle = '#292825'
  ctx.beginPath()
  ctx.arc(current.origin.x, current.origin.y - 8, 16, 0, Math.PI * 2)
  ctx.fill()
  ctx.fillStyle = '#A94B3C'
  ctx.fillRect(current.origin.x - 14, current.origin.y + 6, 28, 10)

  const tip = hookTip(current)
  ctx.strokeStyle = '#292825'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(current.origin.x, current.origin.y + 16)
  ctx.lineTo(tip.x, tip.y)
  ctx.stroke()
  ctx.fillStyle = '#683E3D'
  ctx.beginPath()
  ctx.arc(tip.x, tip.y, 5, 0, Math.PI * 2)
  ctx.fill()

  const drawItem = (item, hooked) => {
    if (item.kind === 'tnt') {
      ctx.fillStyle = '#A94B3C'
      ctx.beginPath()
      ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2)
      ctx.fill()
      ctx.fillStyle = '#F8F6F0'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('TNT', item.x, item.y)
      return
    }
    if (item.kind === 'bag') {
      ctx.fillStyle = '#8B877D'
      ctx.beginPath()
      ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2)
      ctx.fill()
      ctx.strokeStyle = '#292825'
      ctx.stroke()
      ctx.fillStyle = '#F8F6F0'
      ctx.font = '11px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('袋', item.x, item.y)
      return
    }
    const img = loadImage(item.filename)
    const size = item.radius * 2
    ctx.save()
    ctx.beginPath()
    ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2)
    ctx.clip()
    if (img.complete && img.naturalWidth) {
      ctx.drawImage(img, item.x - item.radius, item.y - item.radius, size, size)
    } else {
      ctx.fillStyle = '#C4B5A5'
      ctx.fill()
    }
    ctx.restore()
    ctx.strokeStyle = hooked ? '#A94B3C' : 'rgba(41,40,37,0.35)'
    ctx.lineWidth = 1.5
    ctx.beginPath()
    ctx.arc(item.x, item.y, item.radius, 0, Math.PI * 2)
    ctx.stroke()
  }

  for (const item of current.items) drawItem(item, false)
  if (current.grabbed) drawItem(current.grabbed, true)
}

let raf = 0
let lastTs = 0

function loop(ts) {
  raf = requestAnimationFrame(loop)
  if (document.hidden) {
    lastTs = 0
    return
  }
  const current = run.value
  const ctx = canvasRef.value?.getContext('2d')
  if (!current || !ctx) return
  if (!lastTs) lastTs = ts
  const dt = Math.min(0.05, (ts - lastTs) / 1000)
  lastTs = ts
  const before = current.phase
  tick(current, dt)
  if (before !== current.phase && (current.phase === 'fail' || current.phase === 'daily_done')) {
    settleRun(current)
  }
  draw(ctx, current)
}

watch(() => store.images.length, (n) => {
  if (n && !run.value?.items?.length) startRun()
})

watch(phase, (next, prev) => {
  if (next === 'fail' || next === 'daily_done') {
    if (run.value) settleRun(run.value)
  }
  if (prev && next && prev !== next) lastTs = 0
})

onMounted(async () => {
  reduceMotion.value = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  syncBoardDate()
  await store.fetchImages()
  startRun()
  lastTs = 0
  raf = requestAnimationFrame(loop)
})

onUnmounted(() => {
  cancelAnimationFrame(raf)
})

function switchMode(next) {
  mode.value = next
  startRun()
}

const timeLabel = computed(() => Math.max(0, Math.ceil(run.value?.timeLeft || 0)))
const records = computed(() => board.value.records || [])
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-8">
      <p class="ed-meta mb-4"><span class="ed-num">11</span> Mine</p>
      <h1 class="ed-display">
        Gold, but<br /><em class="italic">frogs.</em>
      </h1>
      <p class="mt-6 text-charcoal max-w-lg">钩子摆动，点一下放出。矿石是奶蛙表情：越大越沉，分越少。过关进店，炸药可丢掉钩上的货。</p>
    </section>

    <section class="ed-page pb-4 flex flex-wrap gap-6 items-center">
      <div class="flex gap-6 ed-meta">
        <button type="button" :aria-pressed="mode === 'arcade'" :class="mode === 'arcade' ? 'text-accent' : ''" @click="switchMode('arcade')">矿场</button>
        <button type="button" :aria-pressed="mode === 'daily'" :class="mode === 'daily' ? 'text-accent' : ''" @click="switchMode('daily')">今日矿洞</button>
      </div>
      <MaximalButton variant="ghost" size="sm" @click="startRun">重开</MaximalButton>
    </section>

    <section class="ed-page pb-4">
      <div class="flex flex-wrap gap-x-8 gap-y-2 ed-meta border-y border-ink/15 py-4">
        <span>Lv {{ run?.level || 1 }}</span>
        <span>Score {{ run?.score || 0 }}</span>
        <span>Goal {{ run?.target || 0 }}</span>
        <span>Time {{ timeLabel }}</span>
        <span>TNT {{ run?.dynamite || 0 }}</span>
      </div>
    </section>

    <section class="ed-page pb-10 relative">
      <p v-if="store.loading" class="ed-meta py-16">Loading plates…</p>
      <div v-else-if="store.error" class="py-16">
        <p class="text-accent mb-4">{{ store.error }}</p>
        <button type="button" class="ed-link" @click="store.fetchImages()">重试</button>
      </div>
      <canvas
        v-show="!store.loading && !store.error"
        ref="canvasRef"
        :width="W"
        :height="H"
        class="w-full max-w-3xl border border-ink/15 bg-paper cursor-crosshair"
        tabindex="0"
        aria-label="矿场。点选矿场后，空格放钩，D 使用炸药。"
        @click="tryFire"
        @keydown="onKey"
      ></canvas>

      <div v-if="phase === 'shop'" class="mt-8 max-w-xl border border-ink/15 p-6 bg-warm-white">
        <p class="ed-meta mb-2">Shop</p>
        <p class="font-display text-2xl mb-4">过关。余额 {{ run.score }}</p>
        <ul class="space-y-3 mb-6">
          <li v-for="item in SHOP" :key="item.id" class="flex items-center justify-between gap-4">
            <div>
              <p class="font-display">{{ item.name }} · {{ item.cost }}</p>
              <p class="ed-meta">{{ item.desc }}</p>
            </div>
            <MaximalButton
              size="sm"
              variant="outline"
              :disabled="run.score < item.cost || (item.id === 'strength' && run.strengthBought)"
              @click="onShopBuy(item.id)"
            >
              买
            </MaximalButton>
          </li>
        </ul>
        <MaximalButton @click="onLeaveShop">下一关</MaximalButton>
      </div>

      <div v-else-if="phase === 'fail'" class="mt-8 max-w-md">
        <p class="ed-meta mb-2">Collapse</p>
        <p class="font-display text-3xl mb-6">{{ run.score }} / {{ run.target }} · 第 {{ run.level }} 关</p>
        <MaximalButton @click="startRun">再挖一次</MaximalButton>
      </div>

      <div v-else-if="phase === 'daily_done'" class="mt-8 max-w-md">
        <p class="ed-meta mb-2">Daily</p>
        <p class="font-display text-3xl mb-2">{{ run.score }} {{ run.score >= run.target ? '过关' : '未达目标' }}</p>
        <p class="ed-meta mb-6">今日最佳 {{ board.todayBest }}</p>
        <MaximalButton @click="startRun">再打今日布局</MaximalButton>
      </div>

      <p class="ed-meta mt-6">点选矿场后，空格放钩 · D 使用炸药</p>
    </section>

    <section v-if="mode === 'daily'" class="ed-page pb-24">
      <p class="ed-meta mb-4">本机记录</p>
      <p v-if="!records.length" class="ed-meta">还没有成绩。</p>
      <ol v-else class="space-y-2 max-w-md">
        <li v-for="(row, i) in records" :key="row.at" class="flex justify-between border-b border-ink/10 py-2 ed-meta">
          <span>{{ String(i + 1).padStart(2, '0') }} · {{ row.date }}</span>
          <span>{{ row.score }}</span>
        </li>
      </ol>
    </section>
  </div>
</template>
