import { loadJson, saveJson } from '@/utils/storage'

const KEY = 'naiwa_tarot_journal_v1'
const LIMIT = 20

export function loadTarotJournal() {
  const items = loadJson(KEY, [])
  return Array.isArray(items) ? items : []
}

export function saveTarotReading(entry) {
  const items = loadTarotJournal()
  items.unshift(entry)
  saveJson(KEY, items.slice(0, LIMIT))
  return items.slice(0, LIMIT)
}
