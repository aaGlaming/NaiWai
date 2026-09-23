import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useImageStore } from './images'

describe('图库筛选', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('按分类和文件名缩小结果，清除后回到全部', () => {
    const store = useImageStore()
    store.images = [
      { filename: 'frog-a.png', category: 'emoji', tags: ['躺'] },
      { filename: 'plate-b.png', category: 'sticker', tags: [] }
    ]

    store.setCategory('emoji')
    expect(store.filteredImages.map(item => item.filename)).toEqual(['frog-a.png'])

    store.setSearch('plate')
    expect(store.filteredImages).toEqual([])

    store.setCategory('all')
    store.setSearch('')
    expect(store.filteredImages).toHaveLength(2)
  })
})
