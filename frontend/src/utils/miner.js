/** Classic gold-miner physics and level generation. Ores are catalog stickers. */

export const RARITY_TABLE = {
  N: { radius: 38, mass: 4.4, value: 20, label: '岩' },
  R: { radius: 28, mass: 2.5, value: 70, label: '银' },
  SR: { radius: 20, mass: 1.5, value: 160, label: '金' },
  SSR: { radius: 14, mass: 0.75, value: 420, label: '钻' }
}

export const SHOP = [
  { id: 'strength', name: '大力', desc: '本局收回更快', cost: 80 },
  { id: 'dynamite', name: '炸药', desc: '丢掉当前钩物并炸开', cost: 100 },
  { id: 'time', name: '加时', desc: '下一关 +15 秒', cost: 70 }
]

const RARITY_ROLL = [
  ['N', 60],
  ['R', 25],
  ['SR', 12],
  ['SSR', 3]
]

export function hashSeed(text) {
  let h = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

export function mulberry32(seed) {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export function rarityFromName(filename) {
  const n = hashSeed(filename) % 100
  let acc = 0
  for (const [rarity, weight] of RARITY_ROLL) {
    acc += weight
    if (n < acc) return rarity
  }
  return 'N'
}

function pickRarity(rng) {
  const n = rng() * 100
  let acc = 0
  for (const [rarity, weight] of RARITY_ROLL) {
    acc += weight
    if (n < acc) return rarity
  }
  return 'N'
}

export function levelTarget(level, daily) {
  if (daily) return 780
  return 380 + level * 220
}

export function levelTime(level, bonus, daily) {
  if (daily) return 90 + bonus
  return 58 + bonus
}

function overlaps(a, b, pad = 8) {
  const dx = a.x - b.x
  const dy = a.y - b.y
  const r = a.radius + b.radius + pad
  return dx * dx + dy * dy < r * r
}

export function generateLevel({ images, level, rng, width, height, originY, daily }) {
  const frogs = images.filter((img) => img.filename)
  const count = daily ? 14 : Math.min(18, 7 + level * 2)
  const items = []
  const minY = originY + 90
  const maxY = height - 28
  const minX = 36
  const maxX = width - 36

  function place(item) {
    for (let attempt = 0; attempt < 60; attempt += 1) {
      item.x = minX + rng() * (maxX - minX)
      item.y = minY + rng() * Math.max(40, maxY - minY)
      if (items.every((other) => !overlaps(item, other))) {
        items.push(item)
        return true
      }
    }
    return false
  }

  const specials = daily || level % 2 === 1 ? 1 : 0
  if (rng() < 0.85) {
    place({ id: 'tnt', kind: 'tnt', radius: 18, mass: 1, value: 0 })
  }
  if (rng() < 0.7 || specials) {
    place({ id: 'bag', kind: 'bag', radius: 16, mass: 1.1, value: 0 })
  }

  let i = 0
  while (items.filter((it) => it.kind === 'ore').length < count && i < count * 8) {
    i += 1
    if (!frogs.length) break
    const img = frogs[Math.floor(rng() * frogs.length)]
    const rarity = img.rarity && RARITY_TABLE[img.rarity] ? img.rarity : pickRarity(rng)
    const spec = RARITY_TABLE[rarity]
    place({
      id: `ore-${items.length}-${img.filename}`,
      kind: 'ore',
      filename: img.filename,
      rarity,
      radius: spec.radius,
      mass: spec.mass,
      value: spec.value
    })
  }
  return items
}

export function createRun({ mode, images, width, height, reduceMotion, seed }) {
  const rng = mulberry32(seed ?? (Math.floor(Math.random() * 2 ** 32) >>> 0))
  const origin = { x: width / 2, y: 64 }
  const daily = mode === 'daily'
  const run = {
    mode,
    width,
    height,
    origin,
    reduceMotion: !!reduceMotion,
    rng,
    images,
    level: 1,
    score: 0,
    strength: 1,
    dynamite: 0,
    nextBonusTime: 0,
    strengthBought: false,
    phase: 'idle',
    timeLeft: 0,
    target: 0,
    items: [],
    angle: 0,
    length: 28,
    swingT: 0,
    grabbed: null,
    tracked: false
  }
  startLevel(run)
  return run
}

export function startLevel(run) {
  run.phase = 'idle'
  run.length = 28
  run.grabbed = null
  run.swingT = 0
  run.target = levelTarget(run.level, run.mode === 'daily')
  run.timeLeft = levelTime(run.level, run.nextBonusTime, run.mode === 'daily')
  run.nextBonusTime = 0
  run.items = generateLevel({
    images: run.images,
    level: run.level,
    rng: run.rng,
    width: run.width,
    height: run.height,
    originY: run.origin.y,
    daily: run.mode === 'daily'
  })
}

export function hookTip(run) {
  return {
    x: run.origin.x + Math.sin(run.angle) * run.length,
    y: run.origin.y + Math.cos(run.angle) * run.length
  }
}

function maxReach(run) {
  return Math.min(run.height - 20, Math.hypot(run.origin.x, run.height - run.origin.y) - 8)
}

function hitTest(run) {
  const tip = hookTip(run)
  for (const item of run.items) {
    const dx = tip.x - item.x
    const dy = tip.y - item.y
    if (dx * dx + dy * dy <= (item.radius + 7) ** 2) return item
  }
  return null
}

function explodeAt(run, x, y, radius = 78) {
  run.items = run.items.filter((item) => {
    const dx = item.x - x
    const dy = item.y - y
    return dx * dx + dy * dy > radius * radius
  })
}

function collectGrabbed(run) {
  const item = run.grabbed
  run.grabbed = null
  if (!item) return
  if (item.kind === 'tnt') {
    explodeAt(run, item.x, item.y)
    return
  }
  if (item.kind === 'bag') {
    run.score += 40 + Math.floor(run.rng() * 220)
    return
  }
  run.score += item.value
}

export function fireHook(run) {
  if (run.phase !== 'idle') return
  run.phase = 'extend'
}

export function useDynamite(run) {
  if (run.phase !== 'retract' || run.dynamite < 1 || !run.grabbed) return false
  run.dynamite -= 1
  const item = run.grabbed
  run.grabbed = null
  run.items = run.items.filter((it) => it !== item)
  explodeAt(run, item.x, item.y, 70)
  return true
}

export function buyShopItem(run, id) {
  const item = SHOP.find((row) => row.id === id)
  if (!item || run.score < item.cost) return false
  if (id === 'strength' && run.strengthBought) return false
  run.score -= item.cost
  if (id === 'strength') {
    run.strength = 1.5
    run.strengthBought = true
  } else if (id === 'dynamite') {
    run.dynamite += 1
  } else if (id === 'time') {
    run.nextBonusTime += 15
  }
  return true
}

export function leaveShop(run) {
  if (run.phase !== 'shop') return
  run.level += 1
  startLevel(run)
}

function finishLevel(run) {
  if (run.mode === 'daily') {
    run.phase = 'daily_done'
    return
  }
  run.phase = run.score >= run.target ? 'shop' : 'fail'
}

export function tick(run, dt) {
  if (run.phase === 'shop' || run.phase === 'fail' || run.phase === 'daily_done') return

  run.timeLeft -= dt
  if (run.timeLeft <= 0) {
    run.timeLeft = 0
    if (run.phase === 'extend' || run.phase === 'retract') {
      /* finish current pull then judge */
    } else {
      finishLevel(run)
      return
    }
  }

  const amp = run.reduceMotion ? 0.55 : 1.15
  if (run.phase === 'idle') {
    run.swingT += dt
    run.angle = amp * Math.sin(run.swingT * 1.35)
    if (run.timeLeft <= 0) finishLevel(run)
    return
  }

  if (run.phase === 'extend') {
    run.length += 430 * dt
    const hit = hitTest(run)
    if (hit) {
      run.grabbed = hit
      run.items = run.items.filter((it) => it !== hit)
      run.phase = 'retract'
    } else if (run.length >= maxReach(run)) {
      run.phase = 'retract'
    }
    return
  }

  if (run.phase === 'retract') {
    const mass = run.grabbed ? run.grabbed.mass : 0.35
    const speed = (240 * run.strength) / (1 + mass)
    run.length -= speed * dt
    if (run.grabbed) {
      const tip = hookTip(run)
      run.grabbed.x = tip.x
      run.grabbed.y = tip.y
    }
    if (run.length <= 30) {
      run.length = 28
      collectGrabbed(run)
      run.phase = 'idle'
      if (run.timeLeft <= 0) finishLevel(run)
    }
  }
}
