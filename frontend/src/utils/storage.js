export function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

export function saveJson(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* quota / private mode */
  }
}

export function hasSeen(key) {
  return localStorage.getItem(key) === '1'
}

export function markSeen(key) {
  try {
    localStorage.setItem(key, '1')
  } catch {
    /* ignore */
  }
}
