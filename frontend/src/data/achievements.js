import { hasSeen } from '@/utils/storage'

export const ACHIEVEMENTS = [
  { id: 'first_favorite', title: '初次收藏', desc: '收藏第一张奶蛙图', icon: '💖', color: '#A94B3C' },
  { id: 'collector_10', title: '收藏达人', desc: '收藏 10 张奶蛙图', icon: '📚', color: '#292825' },
  { id: 'first_draw', title: '初出茅庐', desc: '完成第一次抽卡', icon: '🎰', color: '#8B877D' },
  { id: 'draw_10', title: '抽卡狂人', desc: '累计抽卡 10 次', icon: '🔥', color: '#A94B3C' },
  { id: 'ssr_get', title: '传说降临', desc: '抽到一张 SSR', icon: '👑', color: '#683E3D' },
  { id: 'wallpaper_1', title: '壁纸大师', desc: '生成第一张壁纸', icon: '🖼️', color: '#8B877D' },
  { id: 'tarot_1', title: '命运占卜', desc: '完成第一次塔罗占卜', icon: '🔮', color: '#A94B3C' },
  { id: 'quiz_1', title: '自我认知', desc: '完成奶蛙心情测试', icon: '🧠', color: '#292825' },
  { id: 'meme_1', title: '梗图制造机', desc: '制作第一张梗图', icon: '😂', color: '#8B877D' },
  { id: 'dex_20', title: '图鉴收集者', desc: '图鉴解锁 20 张', icon: '🐸', color: '#A94B3C' },
  { id: 'match_1', title: '对上了', desc: '完成第一局对对碰', icon: '🎴', color: '#A94B3C' },
  { id: 'checkin_1', title: '今日已躺', desc: '完成第一次签到', icon: '📅', color: '#292825' },
  { id: 'streak_7', title: '一周佛系', desc: '连续签到 7 天', icon: '🧘', color: '#683E3D' },
  { id: 'daily_draw_1', title: '今日赠礼', desc: '领取第一次每日赠抽', icon: '🎁', color: '#A94B3C' },
  { id: 'mine_1', title: '下矿了', desc: '完成第一局黄金矿工', icon: '⛏️', color: '#292825' },
  { id: 'mine_shop', title: '矿场消费', desc: '在局间商店买过一次', icon: '🛒', color: '#8B877D' },
  { id: 'mine_daily', title: '今日矿洞', desc: '打完一次每日矿洞', icon: '🕳️', color: '#A94B3C' }
]

export function checkAchievement(id, state) {
  const s = state.stats || {}
  const fav = state.favorites?.length || 0
  const dex = state.collection?.length || 0

  switch (id) {
    case 'first_favorite': return fav >= 1
    case 'collector_10': return fav >= 10
    case 'first_draw': return s.draws >= 1
    case 'draw_10': return s.draws >= 10
    case 'ssr_get': return s.ssrCount >= 1
    case 'wallpaper_1': return s.wallpapers >= 1
    case 'tarot_1': return s.tarot >= 1
    case 'quiz_1': return s.quiz >= 1
    case 'meme_1': return s.memes >= 1
    case 'dex_20': return dex >= 20
    case 'match_1': return (s.matches || 0) >= 1
    case 'checkin_1': return (s.streak || 0) >= 1 || !!s.lastCheckin
    case 'streak_7': return (s.streak || 0) >= 7
    case 'daily_draw_1': return !!s.lastDailyDraw
    case 'mine_1': return (s.mines || 0) >= 1
    case 'mine_shop': return hasSeen('naiwa_mine_bought')
    case 'mine_daily': return !!s.lastDailyMine
    default: return false
  }
}
