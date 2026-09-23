<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  card: { type: Object, default: null },
  cardBack: { type: String, default: '' },
  revealed: { type: Boolean, default: false },
  reversed: { type: Boolean, default: false },
  index: { type: Number, default: 0 },
  animating: { type: Boolean, default: false },
  position: { type: String, default: '' }
})

const emit = defineEmits(['reveal', 'click'])

const baseUrl = import.meta.env.BASE_URL || '/'
const isRevealed = ref(props.revealed)

// 循环翻转
function handleClick() {
  if (props.card) {
    isRevealed.value = !isRevealed.value
    emit('click')
  }
}

const cardImageUrl = computed(() => {
  if (!props.card) return ''
  return `${baseUrl}images/${props.card.image}`
})

const cardBackUrl = computed(() => {
  if (!props.cardBack) return ''
  return `${baseUrl}images/${props.cardBack}`
})
</script>

<template>
  <button
    type="button"
    class="tarot-card-container"
    :class="{ 'animating': animating }"
    :style="{ '--delay': index * 0.15 + 's' }"
    :aria-pressed="isRevealed"
    :aria-label="isRevealed ? `${position ? `${position}，` : ''}${card?.name || '塔罗牌'}${reversed ? '，逆位' : ''}` : '翻开塔罗牌'"
    @click="handleClick"
  >
    <div
      class="tarot-card-inner"
      :class="{ 'flipped': isRevealed, 'reversed': reversed && isRevealed }"
    >
      <!-- 卡牌背面 -->
      <div class="tarot-card-face tarot-card-back">
        <img
          v-if="cardBackUrl"
          :src="cardBackUrl"
          alt="牌背"
          class="w-full h-full object-cover "
        />
        <div v-else class="w-full h-full bg-warm-white border border-ink/20 flex items-center justify-center">
          <span class="ed-num text-2xl">T</span>
        </div>
      </div>

      <!-- 卡牌正面 -->
      <div class="tarot-card-face tarot-card-front">
        <div class="w-full h-full overflow-hidden border border-ink/20 bg-paper relative">
          <img
            v-if="cardImageUrl"
            :src="cardImageUrl"
            :alt="card?.name || ''"
            class="w-full h-full object-cover"
          />
          <div class="absolute bottom-0 left-0 right-0 bg-ink/80 p-3">
            <p class="text-paper font-display text-sm text-center">{{ card?.name }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 位置标签 -->
    <div v-if="position && isRevealed" class="text-center mt-2">
      <span class="ed-meta text-accent">
        {{ position }}
      </span>
    </div>
  </button>
</template>

<style scoped>
.tarot-card-container {
  display: block;
  border: 0;
  padding: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  perspective: 1000px;
  width: 160px;
  height: 280px;
  cursor: pointer;
  opacity: 0;
  animation: card-appear 0.5s ease forwards;
  animation-delay: var(--delay);
}

.tarot-card-container.animating {
  animation: card-shuffle 0.5s ease;
}

@keyframes card-appear {
  0% { opacity: 0; transform: translateY(-30px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes card-shuffle {
  0% { transform: translateX(0) rotate(0); }
  25% { transform: translateX(-10px) rotate(-5deg); }
  50% { transform: translateX(10px) rotate(5deg); }
  75% { transform: translateX(-5px) rotate(-2deg); }
  100% { transform: translateX(0) rotate(0); }
}

.tarot-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.tarot-card-inner.flipped {
  transform: rotateY(180deg);
}

.tarot-card-inner.reversed.flipped {
  transform: rotateY(180deg) rotateX(180deg);
}

.tarot-card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 2px;
  overflow: hidden;
}

.tarot-card-back {
  z-index: 2;
}

.tarot-card-front {
  transform: rotateY(180deg);
}

.tarot-card-container:hover .tarot-card-inner:not(.flipped) {
  transform: translateY(-5px) rotateY(5deg);
  transition: transform 0.3s ease;
}

@media (max-width: 640px) {
  .tarot-card-container {
    width: 120px;
    height: 210px;
  }
}
</style>
