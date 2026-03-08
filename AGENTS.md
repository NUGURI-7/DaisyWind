## Global User Preferences

1. Prefer production-grade, industry-standard solutions over quick fixes or ad hoc hacks. When a widely accepted standard approach exists, use it instead of inventing a custom workaround.
2. Before writing any code, first describe the intended approach briefly and wait for user approval.
3. If the user's request is ambiguous or missing key details, ask clarifying questions before writing code.
4. 每次开始新任务时，如果存在 `docs/context.md`，先读取它。
5. 每次完成有意义的项目改动后，更新 `docs/context.md`，同步最新的当前状态。
6. 保持 `docs/context.md` 精简：优先重写摘要，只保留最近迭代，并将更早内容压缩进历史摘要。

# DaisyWind — Codex 指南

## 项目结构

- `frontend/` — Vue 3 + Vite + Tailwind CSS v4 + DaisyUI v5
- `main.py` / `backend/` — FastAPI + Tortoise ORM + Redis
- `config.py` — 全局配置（端口、DB、Redis、JWT 等）

## 开发服务器

- 前端：`npm run dev`（`frontend/` 目录下），端口 **7777**
- 后端：`uv run python main.py`，端口 **8000**

## Sidebar 设计规范

### 折叠/展开状态

- 展开宽度：`w-64`（256px）；折叠宽度：`w-14`（56px）
- 过渡：`transition-[width] duration-300ms`
- 状态变体：`is-drawer-open:` / `is-drawer-close:`（CSS 自定义 variant，不是 Vue 响应式）

### 动画原则：图标锚定左侧，sidebar 向右扩展

- 展开/折叠时，所有图标/按钮的**水平位置不变**，只有 sidebar 宽度和文字可见性变化
- **不要用** `is-drawer-close:justify-center`（会让图标跳到中心）
- **不要用** `is-drawer-close:flex-col`（会让布局变成纵向，图标发生位移）
- 顶部栏用 `flex items-center h-14 px-3 gap-3`，收起按钮用 `ml-auto` 推到右侧
- 图标和按钮**不随状态改变尺寸**，`size-*` 类不加 `is-drawer-close:` 前缀

### 菜单项按钮

- 必须设置**固定高度** `h-12`（48px），保证展开/折叠时垂直尺寸不变
- 使用 `flex items-center` 布局（不依赖 DaisyUI menu 默认 `display: block`）
- 始终左对齐，**不加** `is-drawer-close:justify-center`
- SVG 图标：`size-4 shrink-0`，**不加** `my-*` 外边距（flex 负责垂直居中）
- 文字 span：`is-drawer-close:opacity-0 is-drawer-close:w-0 overflow-hidden whitespace-nowrap`
  - 必须同时设 `opacity-0` + `w-0`，否则隐形文字仍占宽度，导致各按钮 hover 背景不一致

### Teleport Dropdown（用户菜单）

- 用 `<Teleport to="body">` 脱离 sidebar 的 `overflow-x-clip` 上下文
- 位置通过 `getBoundingClientRect()` 动态计算，菜单出现在触发按钮正上方

### Logo 区域（折叠交互）

- 折叠时隐藏 toggle 按钮（`is-drawer-close:hidden`）
- Logo img 包裹在 `relative group` 中：hover 时 logo 淡出 (`is-drawer-close:group-hover:opacity-0`)，展开图标叠加淡入 (`is-drawer-close:group-hover:opacity-100`)
- 叠加图标默认 `pointer-events-none`，hover 时 `is-drawer-close:group-hover:pointer-events-auto`

## 图标规范

**项目自身的 UI 统一使用 `@phosphor-icons/vue`，禁止使用任何手写 SVG 或其他图标库。**

> **例外**：第三方组件库（如 Milkdown / Crepe）内部自带的图标，保持原样，不做替换。只通过 CSS 统一颜色即可。

### Vue 模板中使用

```vue
<script setup>
import { PhPlus, PhNotePencil, PhSliders } from '@phosphor-icons/vue'
</script>

<PhNotePencil :size="16" />
```

### CSS mask-image 方式（适合伪元素场景）

仅当无法注入 DOM 时（如 `::before` 内），才用 SVG data URI mask，且 SVG path 必须从 Phosphor 官方图标提取，不自行绘制。

---

## Tailwind / DaisyUI 注意事项

- 使用 Tailwind v4，支持 variant 叠加，如 `is-drawer-close:group-hover:opacity-100`
- DaisyUI menu button 默认 `display: block`，需要手动加 `flex items-center` 才能可靠控制高度
- `overflow-x-clip`（非 `overflow-x-hidden`）：只裁剪水平方向，不影响垂直方向的 dropdown 弹出
