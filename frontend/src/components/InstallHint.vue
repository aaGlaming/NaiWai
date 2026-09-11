<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { hasSeen, markSeen } from '@/utils/storage'

const visible = ref(false)
let deferred = null

function onPrompt(event) {
  event.preventDefault()
  deferred = event
  if (!hasSeen('naiwa_install_dismissed')) visible.value = true
}

function dismiss() {
  visible.value = false
  markSeen('naiwa_install_dismissed')
}

async function install() {
  if (!deferred) return
  deferred.prompt()
  await deferred.userChoice
  deferred = null
  visible.value = false
  markSeen('naiwa_install_dismissed')
}

onMounted(() => {
  window.addEventListener('beforeinstallprompt', onPrompt)
})

onUnmounted(() => {
  window.removeEventListener('beforeinstallprompt', onPrompt)
})
</script>

<template>
  <div
    v-if="visible"
    class="fixed bottom-4 left-4 right-4 md:left-auto md:right-6 md:w-80 z-[70] bg-paper border border-ink/20 p-4"
  >
    <p class="ed-meta mb-2">Install</p>
    <p class="font-display text-xl mb-4">把奶蛙世界装到主屏幕</p>
    <div class="flex gap-4">
      <MaximalButton @click="install">安装</MaximalButton>
      <MaximalButton variant="ghost" @click="dismiss">以后</MaximalButton>
    </div>
  </div>
</template>
