<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { loadImagesCatalog } from '@/utils/fetchJson'
import { useUserStore } from '@/stores/user'
import { usePageMeta } from '@/composables/usePageMeta'

usePageMeta()
const user = useUserStore()
const baseUrl = import.meta.env.BASE_URL || './'

// 壁纸配置
const wallpaperWidth = ref(1920)
const wallpaperHeight = ref(1080)
const bgColor = ref('#181816')
const bgColorOptions = [
  { name: 'Ink', value: '#181816' },
  { name: 'Paper', value: '#F3F0E8' },
  { name: 'Charcoal', value: '#292825' },
  { name: 'Terracotta', value: '#A6624D' },
  { name: 'Olive', value: '#69705A' }
]

// 图片数据
const allImages = ref([])
const imagesLoading = ref(true)
const imagesError = ref('')
const selectedImages = ref([])
const canvasRef = ref(null)
const isGenerating = ref(false)
const showPreview = ref(false)

// 尺寸预设
const sizePresets = [
  { name: '桌面 1920×1080', width: 1920, height: 1080 },
  { name: '桌面 2560×1440', width: 2560, height: 1440 },
  { name: '手机 1080×1920', width: 1080, height: 1920 },
  { name: '手机 1440×2560', width: 1440, height: 2560 },
  { name: '平板 2048×2732', width: 2048, height: 2732 },
  { name: '超宽 3440×1440', width: 3440, height: 1440 }
]

// 加载图片列表
async function loadImages() {
  imagesLoading.value = true
  imagesError.value = ''
  try {
    allImages.value = await loadImagesCatalog(baseUrl)
  } catch (e) {
    imagesError.value = e.message || '无法加载图片列表'
  } finally {
    imagesLoading.value = false
  }
}

// 切换图片选择
function toggleImage(image) {
  const index = selectedImages.value.findIndex(i => i.filename === image.filename)
  if (index > -1) {
    selectedImages.value.splice(index, 1)
  } else if (selectedImages.value.length < 12) {
    selectedImages.value.push(image)
  }
}

function isSelected(image) {
  return selectedImages.value.some(i => i.filename === image.filename)
}

// 设置尺寸
function setSize(preset) {
  wallpaperWidth.value = preset.width
  wallpaperHeight.value = preset.height
}

// 自动生成功能
async function autoGenerate() {
  if (allImages.value.length === 0) return

  isGenerating.value = true
  selectedImages.value = []

  // 随机选择5-12张图片
  const count = Math.floor(Math.random() * 8) + 5
  const shuffled = [...allImages.value].sort(() => Math.random() - 0.5)
  selectedImages.value = shuffled.slice(0, count)

  await nextTick()
  await generateWallpaper()
  isGenerating.value = false
}

// 生成壁纸
async function generateWallpaper() {
  if (selectedImages.value.length === 0) return

  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  canvas.width = wallpaperWidth.value
  canvas.height = wallpaperHeight.value

  ctx.fillStyle = bgColor.value
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // 轻网格
  ctx.save()
  ctx.strokeStyle = bgColor.value === '#F3F0E8' ? 'rgba(24,24,22,0.08)' : 'rgba(243,240,232,0.08)'
  ctx.lineWidth = 1
  const step = Math.min(canvas.width, canvas.height) * 0.04
  for (let x = 0; x < canvas.width; x += step) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke()
  }
  for (let y = 0; y < canvas.height; y += step) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke()
  }
  ctx.restore()

  // 计算图片布局
  const images = selectedImages.value
  const padding = Math.min(canvas.width, canvas.height) * 0.04
  const gap = padding * 0.75

  let cols, rows
  if (images.length <= 2) { cols = images.length; rows = 1 }
  else if (images.length <= 4) { cols = 2; rows = 2 }
  else if (images.length <= 6) { cols = 3; rows = 2 }
  else if (images.length <= 9) { cols = 3; rows = 3 }
  else { cols = 4; rows = Math.ceil(images.length / 4) }

  const cellWidth = (canvas.width - padding * 2 - gap * (cols - 1)) / cols
  const cellHeight = (canvas.height - padding * 2 - gap * (rows - 1)) / rows

  // 加载并绘制图片
  const loadPromises = images.map((img, index) => {
    return new Promise((resolve) => {
      const imgEl = new Image()
      imgEl.crossOrigin = 'anonymous'
      imgEl.onload = () => {
        const col = index % cols
        const row = Math.floor(index / cols)

        const x = padding + col * (cellWidth + gap)
        const y = padding + row * (cellHeight + gap)

        const scale = Math.min(cellWidth / imgEl.width, cellHeight / imgEl.height)
        const drawWidth = imgEl.width * scale
        const drawHeight = imgEl.height * scale
        const drawX = x + (cellWidth - drawWidth) / 2
        const drawY = y + (cellHeight - drawHeight) / 2

        // 绘制圆角背景
        ctx.save()
        roundRect(ctx, x, y, cellWidth, cellHeight, 2)
        ctx.fillStyle = bgColor.value === '#F3F0E8' ? '#F8F6F0' : 'rgba(248,246,240,0.08)'
        ctx.fill()
        ctx.strokeStyle = bgColor.value === '#F3F0E8' ? '#181816' : '#F3F0E8'
        ctx.lineWidth = 1
        ctx.stroke()
        ctx.restore()

        // 绘制图片
        ctx.save()
        roundRect(ctx, drawX, drawY, drawWidth, drawHeight, 0)
        ctx.clip()
        ctx.drawImage(imgEl, drawX, drawY, drawWidth, drawHeight)
        ctx.restore()

        resolve()
      }
      imgEl.onerror = () => resolve()
      imgEl.src = `${baseUrl}images/${img.filename}`
    })
  })

  await Promise.all(loadPromises)

  // 绘制水印
  ctx.save()
  ctx.font = `${Math.max(16, canvas.width * 0.01)}px "IBM Plex Sans", sans-serif`
  ctx.fillStyle = bgColor.value === '#F3F0E8' ? 'rgba(24,24,22,0.35)' : 'rgba(243,240,232,0.4)'
  ctx.textAlign = 'right'
  ctx.fillText('NAIWA', canvas.width - 30, canvas.height - 30)
  ctx.restore()
}

// 圆角矩形
function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

// 下载壁纸
function downloadWallpaper() {
  const canvas = canvasRef.value
  if (!canvas || selectedImages.value.length === 0) return

  const link = document.createElement('a')
  link.download = `奶蛙壁纸_${wallpaperWidth.value}x${wallpaperHeight.value}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
  user.track('wallpaper')
}

// 预览
function openPreview() {
  showPreview.value = true
}

onMounted(() => {
  loadImages()
})

watch([selectedImages, wallpaperWidth, wallpaperHeight, bgColor], () => {
  if (selectedImages.value.length) generateWallpaper()
}, { deep: true })
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-10">
      <p class="ed-meta mb-4">Studio — Print</p>
      <h1 class="ed-display">壁纸.</h1>
    </section>

    <section class="ed-page pb-24">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <div class="space-y-10 max-lg:order-2 lg:col-span-4">
          <div>
            <h3 class="ed-meta mb-4">Size</h3>
            <div class="space-y-2">
              <button
                v-for="preset in sizePresets"
                :key="preset.name"
                type="button"
                class="block w-full text-left py-2 ed-meta border-b"
                :aria-pressed="wallpaperWidth === preset.width && wallpaperHeight === preset.height"
                :class="wallpaperWidth === preset.width && wallpaperHeight === preset.height ? 'text-accent border-accent' : 'border-ink/10'"
                @click="setSize(preset)"
              >{{ preset.name }}</button>
            </div>
            <p class="ed-meta mt-3">{{ wallpaperWidth }} × {{ wallpaperHeight }}</p>
          </div>

          <div>
            <h3 class="ed-meta mb-4">Ground</h3>
            <button
              v-for="color in bgColorOptions"
              :key="color.name"
              type="button"
              class="flex items-center gap-3 w-full py-2 border-0 bg-transparent text-left cursor-pointer"
              :aria-pressed="bgColor === color.value"
              @click="bgColor = color.value"
            >
              <span class="w-5 h-5 border border-ink/20" :style="{ background: color.value }" />
              <span class="ed-meta" :class="bgColor === color.value ? 'text-accent' : ''">{{ color.name }}</span>
            </button>
          </div>

          <MaximalButton :loading="isGenerating" class="w-full" @click="autoGenerate">自动排版</MaximalButton>
          <MaximalButton v-if="selectedImages.length > 0" variant="ghost" class="w-full" @click="downloadWallpaper">下载壁纸</MaximalButton>
        </div>

        <div class="space-y-8 max-lg:order-1 lg:col-span-8">
          <div class="flex justify-between items-baseline">
            <p class="ed-meta">Select {{ selectedImages.length }}/12</p>
            <button v-if="selectedImages.length > 0" type="button" class="ed-meta hover:text-accent" @click="selectedImages = []">Clear</button>
          </div>
          <p v-if="imagesLoading" class="ed-meta py-16">Loading…</p>
          <div v-else-if="imagesError" class="py-16">
            <p class="text-accent mb-4">{{ imagesError }}</p>
            <button type="button" class="ed-link" @click="loadImages">重试</button>
          </div>
          <p v-else-if="allImages.length === 0" class="ed-meta py-16">没有可选的图片。</p>
          <div v-else class="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2 max-h-[400px] overflow-y-auto">
            <button
              v-for="image in allImages"
              :key="image.filename"
              type="button"
              class="relative aspect-square bg-warm-white overflow-hidden border p-0 cursor-pointer"
              :aria-pressed="isSelected(image)"
              :class="isSelected(image) ? 'border-accent' : 'border-transparent'"
              @click="toggleImage(image)"
            >
              <img :src="`${baseUrl}images/${image.filename}`" :alt="image.filename" class="w-full h-full object-cover" loading="lazy" />
            </button>
          </div>
          <div>
            <p class="ed-meta mb-3">Preview</p>
            <div class="relative bg-ink overflow-hidden" style="aspect-ratio: 16/9;">
              <canvas ref="canvasRef" class="w-full h-full object-contain" />
              <p v-if="selectedImages.length === 0" class="absolute inset-0 flex items-center justify-center ed-meta text-paper">选择图片或自动排版</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
