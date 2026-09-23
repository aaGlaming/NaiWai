<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  image: { type: Object, required: true },
  rarity: { type: String, default: 'N' },
  revealed: { type: Boolean, default: false },
  index: { type: Number, default: 0 },
  falling: { type: Boolean, default: false },
  compact: { type: Boolean, default: false }
})

const emit = defineEmits(['reveal', 'download'])
const isRevealed = ref(props.revealed)

watch(() => props.revealed, (val) => {
  isRevealed.value = val
})

const baseUrl = import.meta.env.BASE_URL || '/'

const rarityConfig = {
  N: { label: 'Ordinary', color: '#8B877D' },
  R: { label: 'Noted', color: '#292825' },
  SR: { label: 'Selected', color: '#683E3D' },
  SSR: { label: 'Cover', color: '#A94B3C' }
}

const config = computed(() => rarityConfig[props.rarity] || rarityConfig.N)

function handleClick() {
  if (!isRevealed.value) {
    isRevealed.value = true
    emit('reveal')
  }
}

function handleDownload(e) {
  e.stopPropagation()
  emit('download')
}
</script>

<template>
  <div
    class="card-container"
    :class="{ compact }"
    :style="{ '--delay': index * 0.08 + 's' }"
  >
    <button
      v-if="!isRevealed"
      type="button"
      class="absolute inset-0 z-10 cursor-pointer border-0 bg-transparent p-0"
      :aria-label="`翻开，${config.label}`"
      @click="handleClick"
    />
    <div class="card-inner" :class="{ flipped: isRevealed }" :aria-hidden="!isRevealed">
      <div class="card-face card-back">
        <span class="ed-num text-2xl" :style="{ color: config.color }">{{ rarity }}</span>
        <span class="ed-meta mt-2">{{ config.label }}</span>
      </div>
      <div class="card-face card-front">
        <img
          :src="`${baseUrl}images/${image.filename}`"
          :alt="image.filename"
          class="card-image"
        />
        <div class="card-footer">
          <span class="ed-meta" :style="{ color: config.color }">{{ config.label }}</span>
          <button type="button" class="ed-meta" @click="handleDownload">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-container {
  position: relative;
  perspective: 1000px;
  width: 180px;
  height: 260px;
  opacity: 0;
  animation: card-appear 0.4s ease forwards;
  animation-delay: var(--delay);
}
@keyframes card-appear {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.5s ease;
  transform-style: preserve-3d;
}
.card-inner.flipped { transform: rotateY(180deg); }
.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border: 1px solid rgba(24, 24, 22, 0.2);
  overflow: hidden;
}
.card-back {
  background: #F8F6F0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.card-front {
  transform: rotateY(180deg);
  background: #F8F6F0;
  display: flex;
  flex-direction: column;
}
.card-image {
  flex: 1;
  width: 100%;
  object-fit: cover;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-top: 1px solid rgba(24, 24, 22, 0.12);
}
.card-container.compact {
  width: 140px;
  height: 200px;
}
@media (max-width: 640px) {
  .card-container { width: 140px; height: 200px; }
}
</style>
