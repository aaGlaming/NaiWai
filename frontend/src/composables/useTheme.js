import { ref, watch } from 'vue'
import { loadJson, saveJson } from '@/utils/storage'

const STORAGE_KEY = 'naiwa_theme_v1'
const theme = ref(loadJson(STORAGE_KEY, { mode: 'paper' }).mode === 'ink' ? 'ink' : 'paper')

function applyTheme(mode) {
  document.documentElement.classList.toggle('theme-ink', mode === 'ink')
}

applyTheme(theme.value)

watch(theme, (mode) => {
  applyTheme(mode)
  saveJson(STORAGE_KEY, { mode })
})

export function useTheme() {
  function toggleTheme() {
    theme.value = theme.value === 'ink' ? 'paper' : 'ink'
  }
  return { theme, toggleTheme }
}
