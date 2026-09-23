<script setup>
import { ref, onMounted } from 'vue'
import TarotCard from '@/components/TarotCard.vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import tarotData from '@/data/tarot.json'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'
import { loadTarotJournal, saveTarotReading } from '@/utils/tarotJournal'

usePageMeta()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'

const deck = ref([])
const drawnCards = ref([])
const cardBack = ref('')
const isShuffling = ref(false)
const spreadMode = ref('single')
const allowReversed = ref(false)
const showResult = ref(false)
const currentReading = ref(null)
const journal = ref(loadTarotJournal())

// 洗牌动画
function shuffleDeck() {
  isShuffling.value = true
  drawnCards.value = []
  showResult.value = false
  currentReading.value = null

  // 随机选择牌背
  cardBack.value = tarotData.cardBacks[Math.floor(Math.random() * tarotData.cardBacks.length)]

  // 打乱牌组
  const allCards = [...tarotData.majorArcana, ...tarotData.minorArcana]
  deck.value = allCards.sort(() => Math.random() - 0.5)

  setTimeout(() => {
    isShuffling.value = false
  }, 1500)
}

// 抽牌
function drawCards() {
  if (isShuffling.value || deck.value.length === 0) return

  const count = spreadMode.value === 'single' ? 1 : 3
  const newDrawn = []

  for (let i = 0; i < count; i++) {
    if (deck.value.length > 0) {
      const card = deck.value.pop()
      const isReversed = allowReversed.value && Math.random() < 0.3
      newDrawn.push({
        ...card,
        reversed: isReversed,
        position: spreadMode.value === 'three'
          ? tarotData.spreadMeanings.three[['past', 'present', 'future'][i]]
          : tarotData.spreadMeanings.single[0]
      })
    }
  }

  drawnCards.value = newDrawn

  // 生成解读
  currentReading.value = generateReading(newDrawn)
  journal.value = saveTarotReading({
    at: Date.now(),
    mode: spreadMode.value,
    interpretation: currentReading.value.interpretation,
    names: newDrawn.map(c => c.name)
  })
  user.track('tarot')
}

// 生成解读
function generateReading(cards) {
  const keywords = cards.map(c => c.keywords[Math.floor(Math.random() * c.keywords.length)])
  const names = cards.map(c => c.name)

  let interpretation = ''
  if (cards.length === 1) {
    interpretation = `今日的关键词是「${keywords[0]}」。奶蛙提醒你，保持${keywords[0]}的心态，会有好运降临。`
  } else {
    interpretation = `过去：${names[0]}（${keywords[0]}）→ 现在：${names[1]}（${keywords[1]}）→ 未来：${names[2]}（${keywords[2]}）。奶蛙告诉你，从过去到未来，你需要关注「${keywords[1]}」这个主题。`
  }

  return {
    cards,
    keywords,
    interpretation
  }
}

// 重置
function resetReading() {
  drawnCards.value = []
  showResult.value = false
  currentReading.value = null
  shuffleDeck()
}

// 翻牌完成
function onCardReveal(index) {
  if (spreadMode.value === 'three' && drawnCards.value.length === 3) {
    // 三张牌全部翻完后显示结果
    if (drawnCards.value.every(c => c.revealed)) {
      setTimeout(() => {
        showResult.value = true
      }, 500)
    }
  } else if (spreadMode.value === 'single') {
    setTimeout(() => {
      showResult.value = true
    }, 500)
  }
}

// 卡牌点击（循环翻转）
function onCardClick(index) {
  drawnCards.value[index].revealed = !drawnCards.value[index].revealed
  onCardReveal(index)
}

onMounted(() => {
  shuffleDeck()
})
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-10">
      <p class="ed-meta mb-4">Studio — Reading</p>
      <h1 class="ed-display">塔罗.</h1>
      <p class="mt-6 text-charcoal max-w-md">让奶蛙为你抽一张今日的关键词。</p>
    </section>

    <section class="ed-page pb-24">
      <div class="flex flex-wrap items-center gap-6 mb-12 border-b border-ink/15 pb-6">
        <button
          type="button"
          class="ed-meta pb-1 border-b"
          :class="spreadMode === 'single' ? 'text-accent border-accent' : 'border-transparent'"
          @click="spreadMode = 'single'"
        >单牌</button>
        <button
          type="button"
          class="ed-meta pb-1 border-b"
          :class="spreadMode === 'three' ? 'text-accent border-accent' : 'border-transparent'"
          @click="spreadMode = 'three'"
        >三牌阵</button>
        <label class="ed-meta flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="allowReversed" class="accent-accent" />
          允许逆位
        </label>
        <MaximalButton variant="outline" :loading="isShuffling" @click="shuffleDeck">
          {{ isShuffling ? '洗牌中…' : '洗牌' }}
        </MaximalButton>
        <MaximalButton :disabled="isShuffling || drawnCards.length > 0" @click="drawCards">抽牌</MaximalButton>
        <MaximalButton v-if="drawnCards.length > 0" variant="ghost" @click="resetReading">重来</MaximalButton>
      </div>

      <div class="min-h-[420px] border-t border-ink/10 pt-10">
        <div v-if="drawnCards.length === 0 && !isShuffling" class="py-20">
          <p class="font-display text-3xl mb-2">先洗牌，再抽牌。</p>
          <p class="ed-meta">牌阵 · 洗牌 · 抽取 · 翻开</p>
        </div>

        <div v-if="isShuffling" class="flex flex-wrap items-center justify-center min-h-[180px] gap-3">
          <div v-for="i in 5" :key="i" class="w-12 h-20 sm:w-16 sm:h-28 bg-warm-white border border-ink/15 overflow-hidden">
            <img v-if="cardBack" :src="`${baseUrl}images/${cardBack}`" class="w-full h-full object-cover" alt="" />
          </div>
        </div>

        <div v-if="drawnCards.length > 0 && !isShuffling" class="flex flex-col items-center">
          <div class="flex flex-wrap items-end justify-center gap-8">
            <div v-for="(card, index) in drawnCards" :key="card.id">
              <TarotCard
                :card="card"
                :cardBack="cardBack"
                :reversed="card.reversed"
                :index="index"
                :position="card.position"
                @click="onCardClick(index)"
              />
            </div>
          </div>

          <Transition name="fade">
            <div v-if="showResult && currentReading" class="mt-16 max-w-2xl">
              <p class="ed-meta mb-4">Reading</p>
              <p class="font-display text-2xl md:text-3xl leading-snug">
                {{ currentReading.interpretation }}
              </p>
            </div>
          </Transition>
        </div>
      </div>

      <aside v-if="journal.length" class="mt-20 border-t border-ink/15 pt-10">
        <p class="ed-meta mb-6">Journal</p>
        <ul class="space-y-6 max-w-2xl">
          <li v-for="item in journal" :key="item.at">
            <p class="ed-meta mb-1">{{ new Date(item.at).toLocaleString() }} · {{ item.mode === 'three' ? '三牌' : '单牌' }}</p>
            <p class="text-charcoal">{{ item.interpretation }}</p>
          </li>
        </ul>
      </aside>
    </section>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

</style>
