/**
 * Fetch JSON with timeout — works on GitHub Pages without axios hang.
 */
export async function fetchJson(url, timeoutMs = 8000) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const res = await fetch(url, { signal: controller.signal })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } finally {
    clearTimeout(timer)
  }
}

export async function loadImagesCatalog(baseUrl = import.meta.env.BASE_URL || './') {
  const base = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
  const preferApi = import.meta.env.DEV || !!import.meta.env.VITE_API_BASE

  if (preferApi) {
    try {
      const apiBase = import.meta.env.VITE_API_BASE || ''
      const data = await fetchJson(`${apiBase}/api/images`)
      if (data?.images?.length) return data.images
    } catch (_) { /* fall back to static catalog */ }
  }

  try {
    const data = await fetchJson(`${base}images.json`)
    if (data?.images?.length) return data.images
  } catch (e) {
    throw new Error('无法加载图片列表，请稍后重试')
  }

  return []
}
