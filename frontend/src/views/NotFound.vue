<script setup>
import { usePageMeta } from '@/composables/usePageMeta'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { useRouter } from 'vue-router'

usePageMeta()
const router = useRouter()
</script>

<template>
  <div class="ed-page min-h-[70vh] flex items-end pb-24 pt-20">
    <div class="max-w-xl">
      <p class="ed-meta mb-6">Page not bound</p>
      <h1 class="ed-display mb-6">404</h1>
      <p class="font-display text-2xl mb-4">这页没有装订进本期。</p>
      <p class="text-warm-gray mb-10">也许路径写错，也许奶蛙在空白处睡着了。</p>
      <MaximalButton @click="router.push('/')">回到封面</MaximalButton>
    </div>
  </div>
</template>
