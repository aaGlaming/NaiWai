<script setup>
import { useUserStore } from '@/stores/user'

const props = defineProps({
  filename: { type: String, required: true },
  size: { type: String, default: 'md' }
})

const user = useUserStore()

const sizeClass = {
  sm: 'text-[10px] px-2 py-1',
  md: 'text-[11px] px-2.5 py-1.5',
  lg: 'text-xs px-3 py-2'
}
</script>

<template>
  <button
    type="button"
    class="ed-meta border border-ink/20 bg-paper/90 hover:border-accent hover:text-accent transition-colors duration-200"
    :class="[
      sizeClass[size],
      user.isFavorite(filename) ? 'text-accent border-accent' : 'text-ink'
    ]"
    :title="user.isFavorite(filename) ? '取消收藏' : '收藏'"
    :aria-label="user.isFavorite(filename) ? '取消收藏' : '收藏'"
    :aria-pressed="user.isFavorite(filename)"
    @click.stop="user.toggleFavorite(filename)"
  >
    {{ user.isFavorite(filename) ? 'Saved' : 'Save' }}
  </button>
</template>
