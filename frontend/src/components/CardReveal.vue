<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useModalSession } from '@/composables/useModal'
import { loadImagesCatalog } from '@/utils/fetchJson'

const emit = defineEmits(['close'])
const baseUrl = import.meta.env.BASE_URL || './'
const spreadRef = ref(null)
const resultRef = ref(null)
const visible = ref(true)
const images = ref([])
const revealed = ref([false, false, false, false, false])
const showResult = ref(false)
const allRevealed = computed(() => revealed.value.every(r => r))

async function loadRandomImages() {
  try {
    const list = await loadImagesCatalog(baseUrl)
    const shuffled = [...list].sort(() => Math.random() - 0.5)
    images.value = shuffled.slice(0, 5)
  } catch (e) {
    console.error('Failed to load images:', e)
  }
}

function revealAll() {
  revealed.value = [true, true, true, true, true]
  setTimeout(() => { showResult.value = true }, 600)
}

function revealCard(index) {
  if (!revealed.value[index]) {
    revealed.value[index] = true
    if (allRevealed.value) {
      setTimeout(() => { showResult.value = true }, 600)
    }
  }
}

function downloadImage(image) {
  const link = document.createElement('a')
  link.href = `${baseUrl}images/${image.filename}`
  link.download = image.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function downloadAll() {
  images.value.forEach((img, i) => {
    setTimeout(() => downloadImage(img), i * 300)
  })
}

function closeModal() {
  visible.value = false
  emit('close')
}

useModalSession(() => (showResult.value ? resultRef.value : spreadRef.value), closeModal)

watch(showResult, (on) => {
  if (!on) return
  nextTick(() => resultRef.value?.querySelector('button')?.focus())
})

onMounted(() => {
  loadRandomImages()
})
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" ref="spreadRef" class="fixed inset-0 z-[200] flex flex-col items-center justify-center bg-ink/90" role="dialog" aria-modal="true" aria-label="开屏抽卡" @click.self="closeModal">
        <button type="button" class="ed-meta text-paper mb-10 border-0 bg-transparent cursor-pointer" @click="revealAll">全部翻开</button>
        <div class="flex flex-wrap items-center justify-center gap-4 md:gap-6 px-4 mb-10">
          <div v-for="(image, index) in images" :key="index" class="relative">
          <button
            type="button"
            class="relative w-32 h-48 md:w-40 md:h-60 perspective-1000 bg-transparent border-0 p-0 cursor-pointer"
            :aria-label="`翻开第 ${index + 1} 张`"
            @click="revealCard(index)"
          >
            <div class="relative w-full h-full transition-transform duration-500" :class="{ 'rotate-y-180': revealed[index] }" style="transform-style: preserve-3d;">
              <div class="absolute inset-0 border border-paper/30 bg-charcoal flex flex-col items-center justify-center backface-hidden">
                <span class="ed-num text-paper text-2xl">{{ String(index + 1).padStart(2, '0') }}</span>
              </div>
              <div class="absolute inset-0 border border-paper/30 overflow-hidden rotate-y-180 backface-hidden bg-paper">
                <img :src="`${baseUrl}images/${image.filename}`" alt="" class="w-full h-full object-cover" />
              </div>
            </div>
          </button>
          <button
            v-if="revealed[index]"
            type="button"
            class="absolute bottom-2 right-2 z-10 ed-meta text-paper bg-ink/70 px-2 py-1 border-0 cursor-pointer"
            @click="downloadImage(image)"
          >下载</button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showResult" ref="resultRef" class="fixed inset-0 z-[210] flex items-center justify-center bg-ink/90 p-6" role="dialog" aria-modal="true" aria-labelledby="reveal-result-title">
        <div class="relative max-w-2xl w-full bg-paper p-8 md:p-12">
          <button type="button" class="absolute top-4 right-4 ed-meta" @click="closeModal">Close</button>
          <p class="ed-meta mb-3">Vol. 02</p>
          <h2 id="reveal-result-title" class="font-display text-4xl md:text-5xl mb-8">Five plates.</h2>
          <div class="flex justify-center gap-2 mb-10">
            <div v-for="(image, index) in images" :key="index" class="w-14 h-20 overflow-hidden bg-warm-white">
              <img :src="`${baseUrl}images/${image.filename}`" :alt="image.filename" class="w-full h-full object-cover" />
            </div>
          </div>
          <div class="flex flex-wrap gap-8">
            <button type="button" class="ed-link" @click="downloadAll">全部下载</button>
            <button type="button" class="ed-link" @click="closeModal">进入刊物</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.perspective-1000 { perspective: 1000px; }
.rotate-y-180 { transform: rotateY(180deg); }
.backface-hidden { backface-visibility: hidden; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
