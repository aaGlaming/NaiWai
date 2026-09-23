<script setup>
import { ref } from 'vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { useModalSession } from '@/composables/useModal'

defineProps({
  count: { type: Number, default: 0 }
})

const emit = defineEmits(['confirm', 'skip'])
const root = ref(null)
useModalSession(() => root.value, () => {})
</script>

<template>
  <div ref="root" class="fixed inset-0 z-[120] flex items-center justify-center p-6 bg-ink/70" role="dialog" aria-modal="true" aria-labelledby="merge-title">
    <div class="max-w-md w-full bg-paper p-8 border border-ink/15">
      <p class="ed-meta mb-3">Account</p>
      <h2 id="merge-title" class="font-display text-3xl mb-4">合并本机数据？</h2>
      <p class="text-charcoal mb-8">
        检测到本机有 {{ count }} 条收藏/图鉴记录。合并到当前账号后，游客数据会写入本地 SQLite。
      </p>
      <div class="flex flex-wrap gap-4">
        <MaximalButton @click="emit('confirm')">合并</MaximalButton>
        <MaximalButton variant="ghost" @click="emit('skip')">仅使用云端</MaximalButton>
      </div>
    </div>
  </div>
</template>
