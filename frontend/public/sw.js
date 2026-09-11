const CACHE = 'naiwa-__BUILD_VERSION__'
const IMAGE_CACHE = 'naiwa-images-__BUILD_VERSION__'
const ASSETS = ['./', './index.html', './images.json', './manifest.webmanifest', './favicon.svg', './robots.txt']
const MAX_IMAGES = 80

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE && k !== IMAGE_CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  )
})

async function trimImageCache(cache) {
  const keys = await cache.keys()
  if (keys.length > MAX_IMAGES) {
    await cache.delete(keys[0])
    return trimImageCache(cache)
  }
}

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return
  const url = new URL(e.request.url)
  if (url.origin !== self.location.origin) return

  if (url.pathname.startsWith('/api') || url.pathname.includes('/api/')) {
    e.respondWith(fetch(e.request))
    return
  }

  if (url.pathname.endsWith('images.json') || e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone()
            caches.open(CACHE).then((c) => c.put(e.request, clone))
          }
          return res
        })
        .catch(() => caches.match(e.request))
    )
    return
  }

  const isImage = /\/images\//.test(url.pathname) || /\.(gif|png|jpe?g|webp|svg)$/i.test(url.pathname)
  if (isImage) {
    e.respondWith((async () => {
      const cache = await caches.open(IMAGE_CACHE)
      const cached = await cache.match(e.request)
      try {
        const res = await fetch(e.request)
        if (res.ok) {
          await cache.put(e.request, res.clone())
          await trimImageCache(cache)
        }
        return res
      } catch {
        if (cached) return cached
        throw new Error('offline')
      }
    })())
    return
  }

  e.respondWith(
    caches.match(e.request).then((cached) => {
      const network = fetch(e.request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone()
            caches.open(CACHE).then((c) => c.put(e.request, clone))
          }
          return res
        })
        .catch(() => cached)
      return cached || network
    })
  )
})
