import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const PAGE_META = {
  Home: { title: '奶蛙世界 - 首页', description: '探索奶蛙的奇妙世界，佛系躺平，治愈你的每一天。' },
  About: { title: '关于奶蛙', description: '了解奶蛙的起源故事、特征与文化影响。' },
  Gallery: { title: '图片库', description: '447+ 张奶蛙表情包、贴图与动画素材。' },
  LuckyDraw: { title: '奶蛙抽卡', description: '单抽十连，收集稀有奶蛙卡牌！' },
  Wallpaper: { title: '壁纸生成器', description: '选择奶蛙图片，一键生成专属壁纸。' },
  Tarot: { title: '奶蛙塔罗牌', description: '让奶蛙为你揭示命运的奥秘。' },
  MemeMaker: { title: '梗图制作器', description: '给奶蛙加文字，制作专属表情包。' },
  Collection: { title: '我的图鉴', description: '收藏夹、抽卡图鉴与成就徽章。' },
  Profile: { title: '个人中心', description: '查看奶蛙收藏、图鉴、成就与云端同步状态。' },
  Quiz: { title: '奶蛙心情测试', description: '测测你今天是什么状态的奶蛙。' },
  Pet: { title: '奶蛙桌宠', description: '一只可以拖拽的佛系小奶蛙。' },
  MemoryGame: { title: '对对碰', description: '翻开两张相同的奶蛙，完成一局躺平记忆游戏。' },
  Miner: { title: '奶蛙黄金矿工', description: '钩子摆动，把奶蛙表情当矿石挖上来。' },
  Spread: { title: '漫游', description: '一次只看一张奶蛙，用方向键翻页。' },
  Contact: { title: '联系我们', description: '有问题或建议？欢迎联系奶蛙世界。' },
  Changelog: { title: '更新日志', description: '奶蛙世界功能更新记录。' },
  NotFound: { title: '页面走丢了', description: '这只奶蛙找不到路了…' }
}

export function usePageMeta() {
  const route = useRoute()

  function apply(name) {
    const meta = PAGE_META[name] || PAGE_META.Home
    document.title = meta.title.includes('奶蛙世界') ? meta.title : `${meta.title} | 奶蛙世界`
    let tag = document.querySelector('meta[name="description"]')
    if (!tag) {
      tag = document.createElement('meta')
      tag.name = 'description'
      document.head.appendChild(tag)
    }
    tag.content = meta.description
  }

  onMounted(() => apply(route.name))
  watch(() => route.name, (n) => apply(n))
}

export { PAGE_META }
