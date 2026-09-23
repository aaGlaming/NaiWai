<script setup>
import { computed } from 'vue'
import { formatFilename } from '@/utils'
import FavoriteButton from '@/components/FavoriteButton.vue'

const props = defineProps({
  image: { type: Object, required: true },
  colorIndex: { type: Number, default: 0 },
  index: { type: Number, default: 0 }
})

const emit = defineEmits(['preview', 'download'])

const displayName = computed(() => formatFilename(props.image.filename))
const isAnimated = computed(() =>
  props.image.filename.endsWith('.gif') || props.image.filename.endsWith('.webp')
)

const baseUrl = import.meta.env.BASE_URL || '/'
const imageUrl = computed(() => `${baseUrl}images/${props.image.filename}`)

const categoryBadge = computed(() => {
  const map = {
    emoji: { label: '表情' },
    sticker: { label: '贴图' },
    animation: { label: '动画' }
  }
  return map[props.image.category] || map.sticker
})

const num = computed(() => String(props.index + 1).padStart(2, '0'))

async function handleDownload(e) {
  e.stopPropagation()
  const fileName = props.image.filename

  if ('showSaveFilePicker' in window) {
    try {
      const response = await fetch(imageUrl.value)
      const blob = await response.blob()
      const handle = await window.showSaveFilePicker({
        suggestedName: fileName,
        types: [{
          description: '图片文件',
          accept: { 'image/*': ['.gif', '.png', '.jpg', '.webp'] }
        }]
      })
      const writable = await handle.createWritable()
      await writable.write(blob)
      await writable.close()
    } catch (err) {
      if (err.name !== 'AbortError') fallbackDownload(imageUrl.value, fileName)
    }
  } else {
    fallbackDownload(imageUrl.value, fileName)
  }
}

function fallbackDownload(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <article class="group relative">
    <button
      type="button"
      class="block w-full cursor-pointer border-0 bg-transparent p-0 text-left font-inherit text-inherit"
      @click="emit('preview', image)"
    >
    <div class="ed-img aspect-[3/4] mb-3 relative">
      <img
        :src="imageUrl"
        alt=""
        class="object-contain bg-warm-white"
        loading="lazy"
        decoding="async"
      />
    </div>
    <p class="ed-meta flex items-center justify-between">
      <span>{{ num }} / {{ categoryBadge.label }}</span>
      <span v-if="isAnimated">Moving</span>
    </p>
    <h3 class="font-display text-base mt-1 truncate">{{ displayName }}</h3>
    </button>
    <div
      class="absolute top-2 left-2 right-2 z-10 flex justify-between opacity-100 md:opacity-0 md:group-hover:opacity-100 md:group-focus-within:opacity-100 transition-opacity duration-200"
    >
        <FavoriteButton :filename="image.filename" size="sm" />
        <button
          type="button"
          class="ed-meta text-ink bg-paper/90 px-2 py-1"
          title="下载图片"
          aria-label="下载图片"
          @click="handleDownload"
        >
          Save
        </button>
      </div>
  </article>
</template>
