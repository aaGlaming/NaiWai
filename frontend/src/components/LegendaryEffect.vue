<script setup>
import { ref, onMounted } from 'vue'
import { useModalSession } from '@/composables/useModal'

const emit = defineEmits(['skip', 'complete'])
const showText = ref(false)
const root = ref(null)

function skip() {
  emit('skip')
}

useModalSession(() => root.value, skip)

onMounted(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  showText.value = true
  if (reduce) return
  setTimeout(() => emit('complete'), 2800)
})
</script>

<template>
  <Teleport to="body">
    <button
      ref="root"
      type="button"
      class="fixed inset-0 z-[300] flex items-center justify-center bg-ink border-0 p-0 font-inherit cursor-pointer"
      @click="skip"
    >
      <span v-if="showText" class="text-center px-6">
        <span class="ed-meta text-paper/60 mb-6 block">SSR — Cover story</span>
        <span class="font-display text-paper text-6xl md:text-8xl leading-[0.88] block">
          A cover<br />worth keeping.
        </span>
        <span class="ed-meta text-paper/50 mt-10 block">Enter 或点击继续</span>
      </span>
    </button>
  </Teleport>
</template>
