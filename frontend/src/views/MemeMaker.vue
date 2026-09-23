<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useImageStore } from '@/stores/images'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'
import MaximalButton from '@/components/ui/MaximalButton.vue'

usePageMeta()

const store = useImageStore()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'

const selected = ref(null)
const topText = ref('无所谓')
const bottomText = ref('躺平万岁')
const fontSize = ref(48)
const textColor = ref('#F8F6F0')
const strokeColor = ref('#181816')
const canvasRef = ref(null)
const pickerQuery = ref('')
const fileInput = ref(null)

const pickerImages = computed(() => {
  const q = pickerQuery.value.trim().toLowerCase()
  if (!q) return store.images
  return store.images.filter(img =>
    img.filename.toLowerCase().includes(q) ||
    (img.tags && img.tags.some(t => t.toLowerCase().includes(q)))
  )
})

function selectImage(img) {
  selected.value = img
}

function onLocalFile(event) {
  const file = event.target.files?.[0]
  if (!file || !file.type.startsWith('image/')) return
  selected.value = { filename: file.name, _objectUrl: URL.createObjectURL(file) }
}

async function renderMeme() {
  if (!selected.value || !canvasRef.value) return
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.src = selected.value._objectUrl || `${baseUrl}images/${selected.value.filename}`

  await new Promise((resolve, reject) => {
    img.onload = resolve
    img.onerror = reject
  })

  canvas.width = img.width
  canvas.height = img.height
  ctx.drawImage(img, 0, 0)

  const drawText = (text, yRatio) => {
    if (!text.trim()) return
    const size = fontSize.value
    ctx.font = `900 ${size}px Impact, "Arial Black", sans-serif`
    ctx.textAlign = 'center'
    ctx.lineWidth = size / 12
    ctx.strokeStyle = strokeColor.value
    ctx.fillStyle = textColor.value
    const y = canvas.height * yRatio
    ctx.strokeText(text.toUpperCase(), canvas.width / 2, y)
    ctx.fillText(text.toUpperCase(), canvas.width / 2, y)
  }

  drawText(topText.value, 0.12)
  drawText(bottomText.value, 0.92)
}

watch([selected, topText, bottomText, fontSize, textColor, strokeColor], () => {
  if (selected.value) renderMeme()
})

function downloadMeme() {
  if (!canvasRef.value) return
  const link = document.createElement('a')
  link.download = `奶蛙梗图_${Date.now()}.png`
  link.href = canvasRef.value.toDataURL('image/png')
  link.click()
  user.track('meme')
}

onMounted(() => store.fetchImages())
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-10">
      <p class="ed-meta mb-4">Studio — Typesetting</p>
      <h1 class="ed-display">梗图.</h1>
    </section>

    <section class="ed-page pb-24">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="lg:col-span-6 lg:col-start-7">
          <p class="ed-meta mb-6"><span class="ed-num">02</span> Select</p>
          <label class="block mb-4">
            <span class="ed-meta">搜索文件名</span>
            <input v-model="pickerQuery" type="search" class="ed-input" />
          </label>
          <label class="ed-meta block mb-4">
            或上传本地图片
            <input ref="fileInput" type="file" accept="image/*" class="mt-2 block" @change="onLocalFile" />
          </label>
          <p v-if="store.loading" class="ed-meta">加载中…</p>
          <div v-else-if="store.error" class="py-8">
            <p class="text-accent mb-4">{{ store.error }}</p>
            <button type="button" class="ed-link" @click="store.fetchImages()">重试</button>
            <p class="ed-meta mt-4">也可以上传本地图片。</p>
          </div>
          <p v-else-if="pickerImages.length === 0" class="ed-meta py-8">没有匹配的文件名。换一个词，或上传本地图片。</p>
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2 max-h-[640px] overflow-y-auto">
            <button
              v-for="img in pickerImages"
              :key="img.filename"
              type="button"
              class="aspect-square bg-warm-white p-1 border transition-colors duration-200"
              :class="selected?.filename === img.filename && !selected?._objectUrl ? 'border-accent' : 'border-transparent hover:border-ink/30'"
              @click="selectImage(img)"
            >
              <img :src="`${baseUrl}images/${img.filename}`" :alt="img.filename" class="w-full h-full object-contain" loading="lazy" />
            </button>
          </div>
          <p class="ed-meta mt-3">{{ pickerImages.length }} 张可选</p>
        </div>

        <div class="lg:col-span-6 lg:col-start-1 lg:row-start-1">
          <p class="ed-meta mb-6"><span class="ed-num">01</span> Edit</p>
          <div class="space-y-6 mb-8">
            <label class="block">
              <span class="ed-meta">顶部文字</span>
              <input v-model="topText" class="ed-input" />
            </label>
            <label class="block">
              <span class="ed-meta">底部文字</span>
              <input v-model="bottomText" class="ed-input" />
            </label>
            <label class="block ed-meta">字号 {{ fontSize }}
              <input v-model.number="fontSize" type="range" min="24" max="96" class="w-full mt-2 accent-accent" />
            </label>
            <div class="flex gap-8">
              <label class="ed-meta">文字 <input v-model="textColor" type="color" class="ml-2 align-middle" /></label>
              <label class="ed-meta">描边 <input v-model="strokeColor" type="color" class="ml-2 align-middle" /></label>
            </div>
          </div>
          <div class="bg-ink min-h-[280px] flex items-center justify-center overflow-hidden">
            <canvas v-show="selected" ref="canvasRef" class="max-w-full max-h-[400px]" />
            <p v-if="!selected" class="ed-meta text-paper p-8">先选一张图</p>
          </div>
          <div class="mt-8">
            <MaximalButton :disabled="!selected" @click="downloadMeme">下载梗图</MaximalButton>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
