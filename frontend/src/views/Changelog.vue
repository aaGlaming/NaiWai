<script setup>
import { usePageMeta } from '@/composables/usePageMeta'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import { useRouter } from 'vue-router'

usePageMeta()
const router = useRouter()

const logs = [
  {
    vol: '05',
    date: '11.09.2026',
    title: 'SQLite / Daily draw / Ink',
    items: [
      '后端默认改为本地 SQLite（backend/data/naiwa.db），不再依赖 MySQL',
      '新增：签到后每日赠抽、塔罗手记、墨色主题、PWA 安装提示',
      '优化：抽卡共用图库、保底持久化、图库滚动加载、梗图全库搜索'
    ]
  },
  {
    vol: '04',
    date: '04.09.2026',
    title: 'Play / Check-in / Spread',
    items: [
      '新增：躺平对对碰（/play），配对写入图鉴，记录最佳用时',
      '新增：每日签到与连续天数，叠在首页今日奶蛙',
      '新增：单图漫游（/spread），键盘左右翻页'
    ]
  },
  {
    vol: '03',
    date: '04.09.2026',
    title: 'Editorial 改版',
    items: [
      '视觉从 Neo-Brutalism 转为编辑设计：纸色、墨色、朱砂 accent',
      '导航改为杂志目录，页脚改为末页致谢',
      '保留 v2.1：打包下载、分享、开屏仅首次、去掉 Element Plus'
    ]
  },
  {
    vol: '02',
    date: '02.09.2026',
    title: 'v2.0',
    items: [
      '新增：梗图制作器、心情测试、图鉴收藏、成就系统',
      '新增：奶蛙桌宠、每日一图与佛系语录',
      '修复：图片库在 GitHub Pages 上的加载问题',
      '优化：联系表单 mailto 回退、PWA、SEO'
    ]
  },
  {
    vol: '01',
    date: '01.03.2026',
    title: 'v1.0',
    items: [
      '首页、关于、图片库、抽卡、壁纸、塔罗、联系页',
      '447+ 张奶蛙表情包素材',
      '开屏抽卡与 Enter 揭示'
    ]
  }
]
</script>

<template>
  <div>
    <section class="ed-page pt-16 md:pt-24 pb-8">
      <p class="ed-meta mb-4">Vol. / Date / Notes</p>
      <h1 class="ed-display">Log.</h1>
    </section>

    <section class="ed-page pb-24">
      <article v-for="log in logs" :key="log.vol" class="py-10 border-t border-ink/15">
        <p class="ed-meta mb-3">
          <span class="ed-num">Vol. {{ log.vol }}</span>
          <span class="mx-3">·</span>
          {{ log.date }}
        </p>
        <h2 class="font-display text-3xl md:text-4xl mb-6">{{ log.title }}</h2>
        <ul class="space-y-2 text-charcoal">
          <li v-for="(item, i) in log.items" :key="i">{{ item }}</li>
        </ul>
      </article>
      <div class="pt-10">
        <MaximalButton variant="ghost" @click="router.push('/')">返回封面</MaximalButton>
      </div>
    </section>
  </div>
</template>
