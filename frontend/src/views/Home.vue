<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import MaximalButton from '@/components/ui/MaximalButton.vue'
import DailyFrog from '@/components/DailyFrog.vue'

const router = useRouter()
const heroVisible = ref(false)

const contents = [
  { n: '01', path: '/gallery', label: 'Archive', desc: '四百余帧表情与贴图' },
  { n: '02', path: '/lucky', label: 'Draw', desc: '稀有度与保底，像抽特刊' },
  { n: '03', path: '/meme', label: 'Meme', desc: '上下文字，印刷体玩笑' },
  { n: '04', path: '/wallpaper', label: 'Wallpaper', desc: '排版成可带走的平面' },
  { n: '05', path: '/tarot', label: 'Tarot', desc: '单牌或三牌阵' },
  { n: '06', path: '/quiz', label: 'Quiz', desc: '测一测今日的躺法' },
  { n: '07', path: '/play', label: 'Match', desc: '对对碰：翻开同一只肚子' },
  { n: '08', path: '/mine', label: 'Mine', desc: '黄金矿工：矿石换成奶蛙表情' },
  { n: '09', path: '/spread', label: 'Spread', desc: '一次只看一张，像翻内页' },
  { n: '10', path: '/collection', label: 'Collection', desc: '收藏、图鉴与成就' },
  { n: '11', path: '/about', label: 'Essay', desc: '从 2015 年的那只肚子说起' }
]

const stats = [
  { value: '447+', label: 'Plates' },
  { value: '2015', label: 'Origin' },
  { value: '∞', label: 'Idleness' },
  { value: 'PTT', label: 'First print' }
]

const notes = [
  { title: '佛系躺平', description: '四肢松开，浮在水面上。无所谓是一种编辑立场。' },
  { title: '魔性传播', description: '从论坛到会话框，形象比口号走得更快。' },
  { title: '治愈能量', description: '圆肚子与半闭的眼，把 denseness 从屏幕上拿掉。' },
  { title: '无限变体', description: '同一母题，被反复裁切、加字、再发行。' }
]

const timeline = [
  { year: '2015', event: '奶蛙在台湾 PTT 论坛首次出现' },
  { year: '2016', event: '表情包在大陆社交平台走红' },
  { year: '2020', event: '与「躺平」文化并置，成为视觉符号' },
  { year: '至今', event: '持续被改写，热度未从目录中撤下' }
]

onMounted(() => {
  setTimeout(() => { heroVisible.value = true }, 80)
})
</script>

<template>
  <div>
    <section class="ed-page min-h-[85vh] flex flex-col justify-end pb-16 pt-12 md:pt-20">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-end" :class="heroVisible ? 'opacity-100' : 'opacity-0'" style="transition: opacity 400ms ease;">
        <div class="md:col-span-8">
          <p class="ed-meta mb-6">Issue 04 — 2026</p>
          <h1 class="ed-display">
            日常<br />的另一种<br /><em class="italic">躺法。</em>
          </h1>
        </div>
        <div class="md:col-span-4 md:text-right">
          <p class="font-display text-xl md:text-2xl leading-snug text-charcoal mb-8">
            一本关于奶蛙的数字刊物。<br />可浏览、收藏、抽卡、再发行。
          </p>
          <MaximalButton @click="router.push('/gallery')">进入档案</MaximalButton>
        </div>
      </div>
    </section>

    <hr class="ed-rule-strong opacity-20" />

    <DailyFrog />

    <section class="ed-page py-20 md:py-28">
      <p class="ed-meta mb-4"><span class="ed-num">03</span> Contents</p>
      <hr class="ed-rule mb-2" />
      <button
        v-for="item in contents"
        :key="item.path"
        type="button"
        class="ed-row"
        @click="router.push(item.path)"
      >
        <span class="ed-num">{{ item.n }}</span>
        <span>
          <span class="ed-row-title block">{{ item.label }}</span>
          <span class="text-sm text-warm-gray">{{ item.desc }}</span>
        </span>
        <span class="ed-meta hidden sm:inline">Read</span>
      </button>
    </section>

    <section class="ed-page py-16">
      <p class="ed-meta mb-4"><span class="ed-num">04</span> Figures</p>
      <hr class="ed-rule mb-12" />
      <div class="grid grid-cols-2 md:grid-cols-4 gap-10">
        <div v-for="stat in stats" :key="stat.label">
          <p class="font-display text-4xl md:text-5xl">{{ stat.value }}</p>
          <p class="ed-meta mt-2">{{ stat.label }}</p>
        </div>
      </div>
    </section>

    <section class="ed-page py-20 md:py-28">
      <p class="ed-meta mb-4"><span class="ed-num">05</span> Notes on a figure</p>
      <hr class="ed-rule mb-12" />
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-14">
        <article v-for="(note, i) in notes" :key="note.title">
          <p class="ed-num text-xl mb-3">{{ String(i + 1).padStart(2, '0') }}</p>
          <h3 class="font-display text-3xl mb-3">{{ note.title }}</h3>
          <p class="text-charcoal leading-relaxed">{{ note.description }}</p>
        </article>
      </div>
    </section>

    <section class="ed-page py-20">
      <p class="ed-meta mb-4"><span class="ed-num">06</span> Chronicle</p>
      <hr class="ed-rule mb-2" />
      <div
        v-for="item in timeline"
        :key="item.year"
        class="grid grid-cols-12 gap-4 py-6 border-b border-ink/10"
      >
        <span class="col-span-3 md:col-span-2 ed-meta pt-1">{{ item.year }}</span>
        <p class="col-span-9 md:col-span-10 font-display text-2xl md:text-3xl leading-snug">{{ item.event }}</p>
      </div>
    </section>

    <section class="ed-page py-24 md:py-32">
      <blockquote class="font-display text-3xl md:text-5xl leading-tight max-w-3xl italic">
        “Design is not what it looks like.<br />It is how it lies down.”
      </blockquote>
      <p class="ed-meta mt-8">After a frog — 2026</p>
      <div class="mt-12">
        <MaximalButton variant="ghost" @click="router.push('/lucky')">去抽一张封面 →</MaximalButton>
      </div>
    </section>
  </div>
</template>
