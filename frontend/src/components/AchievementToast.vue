<script setup>
import { watch } from 'vue'
import { useUserStore } from '@/stores/user'

const user = useUserStore()

watch(() => user.pendingToast, (val) => {
  if (val) setTimeout(() => user.clearToast(), 4000)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="toast">
      <div
        v-if="user.pendingToast"
        class="fixed top-20 right-6 z-[200] max-w-sm"
        role="status"
      >
        <button
          type="button"
          class="w-full bg-paper border border-ink/20 p-5 text-left cursor-pointer font-inherit text-inherit"
          @click="user.clearToast()"
        >
          <span class="ed-meta text-accent mb-1 block">Achievement</span>
          <span class="font-display text-2xl leading-tight block">{{ user.pendingToast.title }}</span>
          <span class="text-sm text-warm-gray mt-2 block">{{ user.pendingToast.desc }}</span>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
