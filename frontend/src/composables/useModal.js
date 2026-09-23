import { nextTick, onMounted, onUnmounted, watch } from 'vue'

const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'

let pageHolds = 0
let headerHolds = 0

function setInert(id, on) {
  const el = document.getElementById(id)
  if (el) el.inert = on
}

function holdInert({ header = true } = {}) {
  pageHolds += 1
  setInert('page-content', true)
  if (header) {
    headerHolds += 1
    setInert('site-header', true)
  }
  return () => {
    pageHolds = Math.max(0, pageHolds - 1)
    setInert('page-content', pageHolds > 0)
    if (header) {
      headerHolds = Math.max(0, headerHolds - 1)
      setInert('site-header', headerHolds > 0)
    }
  }
}

function focusables(root) {
  const items = [...root.querySelectorAll(FOCUSABLE)]
  if (root.matches?.(FOCUSABLE)) items.unshift(root)
  return items
}

function focusFirst(root) {
  if (!root) return
  const first = focusables(root)[0]
  if (first) first.focus()
  else {
    root.setAttribute('tabindex', '-1')
    root.focus()
  }
}

function trapTab(event, root) {
  if (event.key !== 'Tab' || !root) return
  const items = focusables(root)
  if (!items.length) return
  const first = items[0]
  const last = items[items.length - 1]
  const active = document.activeElement
  if (event.shiftKey && (active === first || !root.contains(active))) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && (active === last || !root.contains(active))) {
    event.preventDefault()
    first.focus()
  }
}

function bindModal(getRoot, onClose, { header = true, trap = true } = {}) {
  let release = null
  let previous = null

  function onKey(event) {
    const root = getRoot()
    if (event.key === 'Escape') {
      event.preventDefault()
      event.stopPropagation()
      onClose()
      return
    }
    if (trap) trapTab(event, root)
  }

  function activate() {
    previous = document.activeElement
    release = holdInert({ header })
    document.addEventListener('keydown', onKey, true)
    nextTick(() => focusFirst(getRoot()))
  }

  function deactivate() {
    document.removeEventListener('keydown', onKey, true)
    release?.()
    release = null
    const back = previous
    previous = null
    if (back && typeof back.focus === 'function') back.focus()
  }

  return { activate, deactivate }
}

export function useModal(openRef, rootRef, onClose, options) {
  const session = bindModal(() => rootRef.value, onClose, options)
  let held = false

  watch(openRef, (open) => {
    if (open && !held) {
      held = true
      session.activate()
    } else if (!open && held) {
      held = false
      session.deactivate()
    }
  }, { flush: 'post', immediate: true })

  onUnmounted(() => {
    if (!held) return
    held = false
    session.deactivate()
  })
}

export function useModalSession(getRoot, onClose, options) {
  const session = bindModal(getRoot, onClose, options)
  onMounted(() => session.activate())
  onUnmounted(() => session.deactivate())
}
