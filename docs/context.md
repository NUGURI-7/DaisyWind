# DaisyWind Context

## 项目概述
- DaisyWind 是一个个人独立开发的 full-stack 项目，前端使用 Vue 3，后端使用 FastAPI。
- 当前产品形态是一个带认证能力的应用壳，核心入口包括 Chat 和 Notes。
- 这个文件是后续 AI 新对话的单一项目上下文来源。

## 早期方向参考（低权重）
- 这部分只用于提供产品方向上的大致印象，帮助 AI 理解项目可能的长期演化方向。
- 这不是正式需求，不构成强约束，也不代表相关能力已经实现。
- 如果与当前代码现状、你在当次对话中的明确要求或后续决策冲突，应以实际项目状态和当前任务为准。
- 目前可以暂时将 DaisyWind 理解为一个面向个人使用场景的智能 AI Agent 助手项目。
- 它的整体方向不是停留在传统的一问一答式对话工具上，而是希望逐步演化为一个更具主动性、可调用工具、可协助处理任务，并能够沉淀用户有效信息的个人智能助手。
- 当前这段描述主要用于提供产品方向上的粗略印象，不应视为固定产品定义；后续产品形态、能力边界和知识沉淀方式仍可能随着开发持续调整。

## 技术栈
- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Tailwind CSS v4, shadcn-vue (Reka UI v2), `@phosphor-icons/vue`
- Frontend editor: Milkdown Crepe
- Backend: FastAPI, Tortoise ORM, Redis, PostgreSQL, JWT auth
- Python tooling: `uv`, Aerich
- Frontend dev server: 在 `frontend/` 目录运行 `npm run dev`，端口 `7777`
- Backend dev server: 运行 `uv run python main.py`，端口 `8000`
- API prefix: `/api/nuguri`

## 当前已有功能
- 已有注册页，包含基础 client-side 校验和注册成功后跳转登录页。
- 已有登录页，接入 auth store，支持 token 写入 `localStorage` 和登录后跳转。
- auth store 支持获取 current user 信息和 logout；当前 user 信息已包含 `last_login` 和 `login_count`。
- 主应用布局采用可折叠 sidebar（Flexbox + data-[collapsed] 驱动）。
- sidebar 包含 Chat、Notes 和 Settings（Theme Switcher Popover）入口。
- sidebar 底部用户菜单已通过 `Teleport` 脱离 overflow 裁剪上下文。
- Notes 模块（P1 已完成）：`api/note.ts` + `stores/notes.ts`（Pinia，autosave debounce + race condition 保护）+ `views/notes/index.vue`（接入 API，可折叠列表面板，AI 面板 toolbar 切换，删除确认）。Milkdown Crepe editor 含代码块折叠/复制反馈、block hover 背景高亮。
- 全局 `btn-ghost` hover 色通过 `--color-btn-ghost-hover` CSS 变量覆盖；sidebar 折叠状态持久化至 `localStorage`。
- Backend Notes CRUD 接口已完成（列表、新建、详情、更新、软删除），路由注册在 `/api/nuguri/note/notes`；title 和 preview 由后端从 content 自动提取。
- Backend 已有用户注册、登录、获取 current user 的接口。
- Backend 登录流程当前会更新用户的 `last_login` 和 `login_count`。
- Backend 生命周期已经接入 Redis 和 PostgreSQL 连接初始化。
- Backend 里已有用于 Redis 和 DB 测试的 playground 路由。

## 已完成：daisyUI → shadcn-vue 迁移
- **迁移原因**：daisyUI 的全局语义色系统难以做出 Claude 风格的定制化 UI
- **目标**：引入 shadcn-vue（基于 Reka UI v2），建立暖色调 CSS 变量主题，逐步替换所有 daisyUI 组件
- **当前进度**：全部 Phase (0~5) 均已完成。daisyUI 已被彻底卸载与移除。
  - `docs/design-tokens.md` — 完整的 11 项设计规范文档，确立了暖色体系。
  - `frontend/src/app.css` — 移除了 daisyUI 配置，完全由 Tailwind v4 与 css-variables 驱动。
  - `views/login`、`views/register`、`views/notes`、`components/chat`、`layout/Sidebar` 均已成功用 shadcn-vue 与原生 Tailwind v4 重写。
- **关键约束**：Tailwind v4（CSS-based config，无 tailwind.config.js）、图标用 @phosphor-icons/vue、不引入 Radix Vue（用 Reka UI v2）

## 其他进行中
- Chat 模块目前有页面结构，但产品行为还不适合视为稳定完成。
- Settings 入口已接入 ThemeSwitcher（Popover 弹出，含 12 主题色 + Light/Dark 切换）。

## 下一步
- Notes 图片上传方案（Phase Two）：目前图片以 base64 嵌入 content，待接入本地磁盘存储 + Cookie 鉴权 serve。

## 开发注意事项
- 项目 UI 统一使用 `@phosphor-icons/vue`，不要引入手写 SVG 或第二套 icon library。
- 这个 context 文件应该保持紧凑，服务于 AI 快速读取，而不是承担完整项目历史归档。

## 维护规则
- 这个文件只保留当前仍然有效的项目状态。
- 更新时优先重写摘要，不要机械地无限追加内容。
- `最近迭代` 只保留最近 8 次以内的记录。
- 旧的迭代信息应压缩进 `历史摘要`，不要让全文持续变长。
- 如果某次改动不足以影响项目理解，就不要把噪音写进来。

## 最近迭代
### 2026-03-13（主题系统：12 主题色 + Light/Dark 切换）
- 新增 `composables/useTheme.ts`：管理主题状态（theme name + dark mode），localStorage 持久化。
- 新增 `components/ThemeSwitcher.vue`：色块网格 + Light/Dark 切换面板。
- `app.css` 新增 11 套主题变量（Neutral/Zinc/Gray/Slate + Rose/Red/Orange/Green/Blue/Yellow/Violet），每套含 light + dark。
- Sidebar Settings 按钮接入 shadcn-vue Popover，弹出 ThemeSwitcher。
- `App.vue` 启动时调用 `applyTheme()` 恢复上次主题选择。

### 2026-03-12（Phase 5: 最终清理与移除 daisyUI）
- 从 `package.json` 彻底卸载了 `daisyui` 和无用的 `@headlessui/vue`。
- 从 `app.css` 中移除了 `@plugin "daisyui"` 和所有的 fallback 主题变量。
- 清理了 `components.json` 中的遗留图标配置，修改为项目标准的 `phosphor`。
- 移除了迁移过程中产生的临时 Python 脚本。
- **DaisyWind 现已完全由 shadcn-vue 和原生 Tailwind CSS v4 驱动。全量迁移宣布圆满成功！**

### 2026-03-12（Phase 4: Sidebar 和 AppLayout 重构完成）
- 彻底移除了 daisyUI 的 `drawer`、`drawer-toggle` 及其他辅助 CSS，将全局布局变更为纯原生 Flexbox + Fixed 遮罩层混合架构。
- 将 `Sidebar.vue` 内部所有的 `is-drawer-*` 自定义 CSS Variants 替换为了基于 Tailwind v4 原生支持的 `group/sidebar` 和 `data-[collapsed]` 属性驱动方案，大幅降低了耦合度。
- 在移动端（小屏）环境重写了 `Sidebar` 逻辑，采用绝对定位并配有交互式黑色半透明 Backdrop，实现标准抽屉体验。
- 集成了 `shadcn-vue` 的 `Tooltip` 组件，确保折叠状态下悬浮提示稳定工作。
- 移除了冗余的 `home-page` 路由页面。

### 2026-03-12（Phase 3: Chat 模块和 MainContent 迁移至 shadcn-vue）
- 移除了 `ChatPanel.vue` 中所有原 daisyUI 的气泡宏类 (`chat-start/end/bubble`)。
- 使用原生的 Tailwind Flex 布局手写了贴合 Claude 极简风格的聊天气泡（`bg-muted` vs `bg-primary`）。
- 替换了底部的输入区组件为 shadcn-vue 的 `Input` 和 `Button`，并加上了更精致的顶部边框分割。
- `MainContent.vue` 的背景色（含渐变遮罩 `from-background`）顺利由 semantic token 接管。

### 2026-03-12（Phase 2: Notes 页面迁移至 shadcn-vue）
- 批量替换了 `views/notes/index.vue` 中近 50 处 daisyUI 颜色/结构工具类为 shadcn-vue 变量（如 `bg-base-100` -> `bg-background`，`border-base-300` -> `border-border` 等）。
- 移除了依赖于 daisyUI 的原 `<dialog class="modal">` 逻辑，并重构为响应式的 shadcn-vue `AlertDialog` 组件。
- 替换了 Milkdown/Crepe CSS 主题重写中对应的原生 CSS 变量绑定，实现对当前主应用色彩的无缝继承。
- 通过了 Tailwind 和 Vue 编译，验证了所有的 CSS 类替换及弹窗逻辑无误。

### 2026-03-12（Phase 1: Login & Register 迁移至 shadcn-vue）
- 验证了前端 Tailwind v4 build 无报错。
- 通过 `npx shadcn-vue@latest init` 成功初始化项目（配置 Base Color: Stone，CSS Variables 开启，New York style）。
- 解决了 tsconfig `baseUrl` 和 alias 解析问题以支持 init 工具。
- 下载并集成 `shadcn-vue` 基础组件（Card, Input, Button, Label, Separator）。
- 将 `views/login/index.vue` 和 `views/register/index.vue` 从 daisyUI 彻底重构为 `shadcn-vue` 体系，使用 `bg-background`, `text-foreground` 等新 CSS 变量。
- Phase 1 顺利完成，验证 build 成功。下一步将进入 Phase 2（迁移 Notes 页面）。

### 2026-03-12（daisyUI → shadcn-vue 迁移启动）
- 完成迁移评估：7 个 Vue 文件 + 1 个 CSS 文件，~140 处 daisyUI 触点。
- 完成 Phase 0（设计规范）：新建 `docs/design-tokens.md`（11 项规范），重写 `app.css` 添加 shadcn-vue CSS 变量体系。
- 确定共存策略：daisyUI `@plugin` 保留，新变量命名空间不冲突。
- 确定 5 阶段渐进式迁移计划（Login → Notes → Chat → Sidebar → 清理）。
- shadcn-vue 尚未安装，组件尚未迁移。

### 2026-03-10（Notes UI 深度打磨与 Bug 修复）
- 移除了全局的 `btn-ghost` 依赖，改用纯 Tailwind v4 工具类构建精致 hover。
- 优化了 Notes 列表交互（左侧高亮指示线，Hover 微移，时间重排）。
- 引入 URL 驱动状态，通过 `vue-router` 将 `selectedId` 绑定至 URL query，解决刷新和路由切换时的状态丢失问题。
- 重绘了无笔记选中时的右侧引导空状态（Empty State）组件。
- 为保存状态指示器增加了旋转与 2 秒后消散的 Tailwind 渐变动画。

### 2026-03-10（Notes 前端 P1 完成 + UI 打磨）
- 完成 Notes 前端重构：`api/note.ts`、`stores/notes.ts`（Pinia）、`index.vue` 接入 API。
- Notes 列表面板可折叠；AI 面板可通过 toolbar PhLayout 按钮切换（默认收起）。
- block hover 改为背景变色；纯文本代码块颜色修正为 `--color-base-content`。
- 全局 `btn-ghost` hover 色通过 CSS 变量统一覆盖（`app.css`）。
- sidebar 折叠状态持久化至 `localStorage`，刷新不丢失。
- 后端 Notes 路由修正（`/list`、`/create` 替换空路径，规避 FastAPI trailing slash 冲突）。

### 2026-03-08（Notes 后端）
- Notes 模块完成后端 CRUD：Note model（软删除）、NoteService、5 个 REST 接口、路由注册。
- title 和 preview 由后端从 content 自动提取，前端只传 content。
- 确定了 Notes 图片方案：本地磁盘存储 + Cookie 鉴权 serve（第二阶段实现）。

### 2026-03-08
- 登录相关 user 信息扩展为包含 `last_login` 和 `login_count`，后端登录流程会同步更新这两个字段。
- Notes editor 增加了代码块折叠和复制成功反馈交互。
- 建立了 `docs/context.md`，作为后续 AI 新对话优先读取的单一项目上下文文件。
- 定义了轻量维护策略：重写当前状态、仅保留最近迭代、将更早历史压缩为摘要。
- 根据当前真实代码结构整理了第一版项目上下文，包括 frontend routes、auth flow、sidebar 行为、notes editor 和 backend API 基础能力。

## 历史摘要
- 早期 backend 基础已经具备 FastAPI app 启动、Redis/PostgreSQL 生命周期接入、Tortoise ORM 模型和 auth 相关服务。
- frontend 基础已经具备 login/register 流程、主布局、可折叠 sidebar 以及 notes editor 页面。

## 后续使用方式
- 每次开启新的 AI 对话时，先读取这个文件。
- 每次完成有意义的开发后，更新这个文件一次。
- 可以直接用类似 `更新 context`、`把这次改动写入 context`、`压缩 context` 的指令触发维护。
