# 🐸 奶蛙世界 - Milk Frog World

一个以 Neo-Brutalism 设计风格为特色的奶蛙介绍网站，展示 448+ 张奶蛙表情包，并提供抽卡、塔罗占卜、梗图制作、心情测试、成就系统、桌宠等丰富的互动功能，支持 PWA 离线访问。

A fan-made website dedicated to the "Milk Frog" internet meme, featuring Neo-Brutalism design, 448+ sticker images, and rich interactive features — gacha draws, tarot readings, meme maker, personality quiz, achievements, desktop pet — with PWA offline support.

## ✨ 项目特点 / Features

- 🖼️ **448+ 张奶蛙表情包** - 精心收集的奶蛙/变异奶龙表情图库，支持分类与搜索
- 🎨 **Neo-Brutalism 设计系统** - 粗黑边框、硬阴影、奶油色背景
- 🎮 **抽卡系统** - 四档稀有度 + 保底机制 + 十连保底
- 🔮 **塔罗牌占卜** - 单牌/三牌牌阵，支持逆位解读
- 🖌️ **梗图制作器** - Canvas 生成经典上下文字梗图
- 🧠 **心情测试** - 5 道题测出你的奶蛙人格
- 🏆 **成就系统** - 10 枚徽章记录你的探索足迹
- 🐸 **桌宠** - 可拖拽漂浮的小奶蛙，随机冒出佛系语录
- 🖼️ **壁纸生成器** - Canvas 自动排布生成高清壁纸
- 📖 **图鉴收藏** - 收藏夹 + 抽卡图鉴，localStorage 持久化
- 📱 **PWA 支持** - Service Worker 缓存，可离线访问
- 🔍 **SEO 优化** - 动态页面标题与描述

## 🛠️ 技术栈 / Tech Stack

| 层级 Layer | 技术 Technology |
|-----------|----------------|
| 前端 Frontend | Vue 3 + Vite 8 + Element Plus + Tailwind CSS 4 |
| 状态管理 State | Pinia 4 |
| 路由 Router | Vue Router 4 (Hash 模式，13 条路由) |
| 后端 Backend | FastAPI (Python) |
| 数据库 Database | MySQL 8 + SQLAlchemy 2 + Alembic |
| 认证 Auth | HttpOnly Cookie + JWT + Argon2 |
| PWA | Manifest + Service Worker (stale-while-revalidate) |
| 设计系统 Design | Neo-Brutalism |
| 字体 Font | Space Grotesk |

## 📁 项目结构 / Project Structure

```
NAIWA/
├── frontend/                    # Vue 3 前端项目
│   ├── src/
│   │   ├── components/          # 组件
│   │   │   ├── ui/              # 可复用 UI 组件
│   │   │   │   ├── MaximalButton.vue    # 按钮组件
│   │   │   │   ├── MaximalCard.vue      # 卡片容器
│   │   │   │   ├── ImageCard.vue        # 图片展示
│   │   │   │   ├── SectionTitle.vue     # 章节标题
│   │   │   │   └── FloatingShape.vue    # 浮动装饰
│   │   │   ├── CardReveal.vue           # 开屏抽卡揭示动画
│   │   │   ├── DailyFrog.vue            # 每日一图 + 佛系语录
│   │   │   ├── DesktopPet.vue           # 可拖拽桌宠
│   │   │   ├── AchievementToast.vue     # 成就解锁通知
│   │   │   ├── FavoriteButton.vue       # 收藏按钮
│   │   │   ├── DrawCard.vue             # 抽卡卡片
│   │   │   ├── DrawHistory.vue          # 抽卡历史
│   │   │   ├── LegendaryEffect.vue      # SSR 全屏特效
│   │   │   └── TarotCard.vue            # 塔罗牌组件
│   │   ├── views/               # 页面组件（13 个路由）
│   │   │   ├── Home.vue                 # 首页
│   │   │   ├── About.vue                # 关于
│   │   │   ├── Gallery.vue              # 图片库
│   │   │   ├── LuckyDraw.vue            # 抽卡
│   │   │   ├── Wallpaper.vue            # 壁纸生成器
│   │   │   ├── Tarot.vue                # 塔罗牌占卜
│   │   │   ├── MemeMaker.vue            # 梗图制作器
│   │   │   ├── Quiz.vue                 # 心情测试
│   │   │   ├── Collection.vue           # 图鉴收藏
│   │   │   ├── Pet.vue                  # 桌宠介绍
│   │   │   ├── Changelog.vue            # 更新日志
│   │   │   ├── Contact.vue              # 联系
│   │   │   └── NotFound.vue             # 404 页面
│   │   ├── router/index.js      # 路由配置（懒加载）
│   │   ├── stores/
│   │   │   ├── index.js         # 图片目录状态
│   │   │   └── user.js          # 用户系统（收藏/图鉴/成就/统计）
│   │   ├── data/
│   │   │   ├── tarot.json       # 塔罗牌数据（大/小阿卡纳）
│   │   │   ├── achievements.js  # 10 个成就定义
│   │   │   ├── quiz.js          # 心情测试题目与结果
│   │   │   └── quotes.js        # 20 条佛系语录
│   │   ├── composables/
│   │   │   └── usePageMeta.js   # 动态 SEO 标题/描述
│   │   ├── utils/
│   │   │   ├── index.js         # 颜色系统、分类识别
│   │   │   ├── fetchJson.js     # 带超时的 fetch + 目录加载
│   │   │   └── storage.js       # localStorage 安全封装
│   │   ├── App.vue              # 根组件（导航/CardReveal/桌宠/成就通知）
│   │   ├── main.js              # 入口（启动即评估成就 + 注册 SW）
│   │   └── style.css            # 全局样式（Neo-Brutalism 设计系统）
│   ├── public/
│   │   ├── images.json          # 图片元数据（GitHub Pages 静态数据源）
│   │   ├── manifest.webmanifest # PWA 清单
│   │   ├── sw.js                # Service Worker（naiwa-v2 缓存）
│   │   └── favicon.svg
│   └── vite.config.js           # Vite 配置（/api、/images 代理）
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── main.py              # 应用入口（CORS、静态文件挂载）
│   │   └── api/
│   │       ├── images.py        # GET /api/images、GET /api/images/{filename}
│   │       └── contact.py       # POST /api/contact
│   └── requirements.txt
├── images/                      # 448+ 张奶蛙图片资源
├── .github/workflows/
│   └── deploy.yml               # GitHub Pages 自动部署
└── README.md
```

## 🗄️ 数据库与账号 / Database & Accounts

项目支持 MySQL 8 云端数据层：账号、图片元数据、收藏、抽卡图鉴、用户统计、成就和留言均可持久化；游客模式仍使用 `localStorage`，首次登录可将本机数据合并到账号。

```bash
cd backend
copy .env.example .env        # 填写 MySQL 连接与随机 SECRET_KEY
pip install -r requirements.txt
python -m alembic upgrade head
python -m scripts.seed_data   # 导入 images.json 与成就定义，可重复执行
```

应用应使用仅授权 `naiwa.*` 的专用 MySQL 用户，不要在 `.env` 中使用 root。数据库结构由 `backend/alembic/` 管理。

本地开发由 Vite 代理 `/api` 到 FastAPI。前后端分开部署时，在前端构建环境设置 `VITE_API_BASE=https://你的-api-域名`，并同步配置后端 `CORS_ORIGINS` 与安全 Cookie。

## 🚀 快速开始 / Quick Start

### 前端开发 / Frontend Development

```bash
cd frontend
npm install
npm run dev        # 开发服务器 http://localhost:5173
```

### 后端开发 / Backend Development

```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端 API 运行在 http://localhost:8000，访问 http://localhost:8000/docs 查看 Swagger 文档。

> 开发环境下 Vite 会将 `/api` 与 `/images` 请求代理到 `http://127.0.0.1:8000`。
> 纯前端模式（无后端）也可运行：页面会自动回退到 `public/images.json` 静态数据。

## 🎨 设计系统 / Design System

### 颜色系统 / Colors

| 名称 Name | 颜色 Color | 用途 Usage |
|-----------|-----------|-----------|
| Background | `#FFFDF5` (Cream White) | 页面背景 |
| Foreground | `#000000` (Black) | 文字和边框 |
| Accent | `#FF6B6B` (Hot Red) | 主要强调色 |
| Secondary | `#FFD93D` (Vivid Yellow) | 次要强调色、按钮、标题背景 |
| Muted | `#C4B5FD` (Soft Violet) | 第三强调色、标签 |

### 字体与阴影 / Typography & Shadows

- **主字体**: Space Grotesk (400/500/700/900)，大写标题、紧凑字间距 (-0.02em)
- **硬阴影**: `.shadow-neo-sm` (4px) / `.shadow-neo` (8px) / `.shadow-neo-lg` (12px) / `.shadow-neo-xl` (16px)，交互时阴影消失 + 元素位移模拟"按下"
- **图案装饰**: `.pattern-dots` 圆点 / `.pattern-grid` 网格 / `.pattern-halftone` 半调 / `.text-stroke` 描边文字

## 📄 页面功能 / Pages (13 Routes)

### 首页 Home (`/`)
英雄区域 + **每日一图与佛系语录**（按日期确定性生成）+ 统计数据 + 特色功能预览 + 时间线。

### 关于 About (`/about`)
奶蛙起源故事、角色特征、使用场景。

### 图片库 Gallery (`/gallery`)
- 448+ 张图片，响应式网格（2-6 列），24 张/页分页
- 分类筛选（emoji / sticker / animation）+ 关键词搜索
- 全屏预览 + 单张下载 + ❤️ 收藏

### 抽卡 Lucky Draw (`/lucky`)
- **稀有度**: N 60% / R 25% / SR 12% / SSR 3%
- **保底**: 连续 10 次未出 SR+ 时必出（80% SR / 20% SSR）；十连至少一张 SR+
- 单抽 / 十连两种模式，逐张揭示或一键全开
- SSR 触发全屏 LegendaryEffect 特效
- 历史记录保存最近 50 次抽取，所有抽到的卡片加入图鉴

### 壁纸生成器 Wallpaper (`/wallpaper`)
- 6 种尺寸预设：1920×1080、2560×1440、1080×1920、1440×2560、2048×2732、3440×1440
- 5 种背景（纯色 + 紫/蓝/粉渐变），最多选择 12 张图片，或"自动生成"随机挑选 5-12 张
- Canvas 自动网格排布 + 圆角卡片 + 角落水印，下载为 PNG

### 塔罗占卜 Tarot (`/tarot`)
- 大/小阿卡纳数据（`tarot.json`），单牌 / 三牌（过去/现在/未来）两种牌阵
- 可选逆位模式（30% 概率），洗牌动画 + 3D 翻牌
- 基于随机关键词自动生成解读文案

### 梗图制作器 MemeMaker (`/meme`)
- 从图库前 60 张中选图，编辑顶部/底部文字
- 自定义字号（24-96px）、文字颜色、描边颜色，实时预览
- Canvas 渲染 Impact 风格字体，下载为 PNG

### 心情测试 Quiz (`/quiz`)
- 5 道情景题，按 lazy / chill / energetic / social 四个维度计分
- 结果为四种奶蛙人格：躺平奶蛙 / 佛系奶蛙 / 元气奶蛙 / 社交奶蛙
- 支持 Web Share API 分享，不支持的浏览器回退到剪贴板复制

### 图鉴收藏 Collection (`/collection`)
- ❤️ 收藏夹：手动收藏的图片
- 🎴 图鉴：抽卡获得的图片集合
- 🏆 成就墙：徽章解锁进度一览

### 桌宠 Pet (`/pet`)
- 桌宠功能介绍页，全局可拖拽小奶蛙的双击入口

### 更新日志 Changelog (`/changelog`)
版本历史与功能演进记录。

### 联系 Contact (`/contact`)
联系表单（后端 API 提交，GitHub Pages 环境回退为 mailto）+ FAQ。

### 404 NotFound (`/:pathMatch(.*)*`)
Neo-Brutalism 风格的 404 页面。

## 🏆 用户系统与成就 / User & Achievements

用户数据由 Pinia store（`stores/user.js`）管理，持久化于 localStorage（`naiwa_user_v1`）：

- **收藏 favorites** / **图鉴 collection**（抽卡获得）/ **统计 stats**（抽卡数、SSR 数、壁纸数、占卜数、测试数、梗图数、下载数）
- `track(event)` 统一埋点，任何状态变化都会触发成就评估
- 10 枚成就徽章：

| 成就 | 条件 |
|------|------|
| 第一次收藏 / 收藏家 | 收藏 ≥ 1 / ≥ 10 |
| 初次抽卡 / 十连战士 | 抽卡 ≥ 1 / ≥ 10 |
| 欧皇认证 | 抽到 SSR |
| 壁纸大师 | 生成第一张壁纸 |
| 佛系占卜 | 第一次塔罗占卜 |
| 心情探索者 | 完成第一次心情测试 |
| 梗图之王 | 制作第一张梗图 |
| 图鉴收藏家 | 图鉴 ≥ 20 |

- 成就解锁时全局弹出 AchievementToast（4 秒自动消失），应用启动时也会补评估

## 🧩 全局体验 / Global Experience

- **CardReveal 开屏动画**: 首次访问弹出 5 张随机卡牌，Enter 一键全开，支持逐张/批量下载
- **DesktopPet 桌宠**: 右下角可拖拽漂浮小奶蛙，点击随机冒出佛系气泡，双击跳转宠物页，显隐状态持久化
- **PWA**: `manifest.webmanifest` 独立窗口模式（主题色 #FFD93D）；Service Worker（缓存名 `naiwa-v2`）预缓存核心资源，同源 GET 请求采用 stale-while-revalidate 策略，仅生产环境注册
- **SEO**: `usePageMeta` 按路由动态设置 `document.title` 与 `<meta name="description">`

## 🚢 部署 / Deployment

### GitHub Pages（自动部署）

推送到 `main` 分支触发 GitHub Actions（`.github/workflows/deploy.yml`）：

1. Node.js 20 环境，`npm ci` + `npm run build`
2. 将根目录 `images/` 复制到 `frontend/dist/images`
3. 经 `actions/deploy-pages@v4` 发布到 GitHub Pages

> GitHub Pages 仅部署前端；后端需单独部署。线上为纯静态模式，数据来自 `images.json`。

### 自定义部署 / Custom Deployment

```bash
# 前端
cd frontend && npm run build   # 产物在 dist/

# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🛠️ 开发指南 / Development Guide

- **Vue 3** Composition API + `<script setup>`，路由组件全部懒加载
- **样式** Tailwind CSS 类名 + `style.css` 中的 Neo-Brutalism 工具类
- **数据** 新增图片时保持 `images/` 文件名与 `public/images.json` 一致
- **状态** 用户相关状态统一走 `user.js` store 并通过 `track()` 埋点

环境要求：Node.js ≥ 18，Python ≥ 3.8。

## 🖼️ 图片资源 / Image Assets

图片来源于网络公开传播的奶蛙/变异奶龙表情图，仅供个人娱乐使用，请勿用于商业用途。

Images are sourced from publicly distributed Milk Frog memes, for personal entertainment only. Do not use for commercial purposes.

## 🤝 贡献 / Contributing

1. Fork 本项目并创建功能分支 (`git checkout -b feature/AmazingFeature`)
2. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
3. 推送分支并创建 Pull Request

## 📝 许可证 / License

个人娱乐项目，非商业用途。Personal entertainment project, non-commercial use only.

---

**Made with 🐸 by NAIWA Team**

## Windows 离线安装包

桌面版内置 Vue 前端、FastAPI 后端、SQLite 和全部图片资源。最终用户无需安装 Python、Node.js 或 MySQL，也无需联网。

- 安装包：`desktop/release/NAIWA-Setup-1.0.0.exe`
- 用户数据：`%LOCALAPPDATA%\NAIWA`
- 数据备份与恢复：应用内“个人中心 → 本地数据管理”
- 完整构建说明：`desktop/README.md`

卸载应用时会保留用户数据库和备份，重新安装后可继续使用。
