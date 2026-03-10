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
- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Tailwind CSS v4, DaisyUI v5, `@phosphor-icons/vue`
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
- 主应用布局采用可折叠的 DaisyUI drawer sidebar。
- sidebar 当前包含 Chat、Notes 和占位中的 Settings 入口。
- sidebar 底部用户菜单已通过 `Teleport` 脱离 overflow 裁剪上下文。
- Notes 模块（P1 已完成）：`api/note.ts` + `stores/notes.ts`（Pinia，autosave debounce + race condition 保护）+ `views/notes/index.vue`（接入 API，可折叠列表面板，AI 面板 toolbar 切换，删除确认）。Milkdown Crepe editor 含代码块折叠/复制反馈、block hover 背景高亮。
- 全局 `btn-ghost` hover 色通过 `--color-btn-ghost-hover` CSS 变量覆盖；sidebar 折叠状态持久化至 `localStorage`。
- Backend Notes CRUD 接口已完成（列表、新建、详情、更新、软删除），路由注册在 `/api/nuguri/note/notes`；title 和 preview 由后端从 content 自动提取。
- Backend 已有用户注册、登录、获取 current user 的接口。
- Backend 登录流程当前会更新用户的 `last_login` 和 `login_count`。
- Backend 生命周期已经接入 Redis 和 PostgreSQL 连接初始化。
- Backend 里已有用于 Redis 和 DB 测试的 playground 路由。

## 正在进行
- Chat 模块目前有页面结构，但产品行为还不适合视为稳定完成。
- Settings 入口目前只是 UI 占位，尚未成为正式页面。
- 当前工作区里仍有部分 frontend 页面和组件处于迭代中。

## 下一步
- Notes 图片上传方案（Phase Two）：目前图片以 base64 嵌入 content，待接入本地磁盘存储 + Cookie 鉴权 serve。
- 明确 Chat 模块当前范围，以及 frontend 和 backend 的集成状态。
- 决定 Settings 是继续延期，还是变成真实页面。
- 需要时补充根目录 `README.md` 的基础运行说明。

## 开发注意事项
- 项目 UI 统一使用 `@phosphor-icons/vue`，不要引入手写 SVG 或第二套 icon library。
- sidebar 折叠行为必须保持图标水平位置固定，避免在侧边栏操作项上使用 `is-drawer-close:justify-center` 和 `is-drawer-close:flex-col`。
- sidebar 菜单项应保持固定高度 `h-12`，并使用 `flex items-center`。
- sidebar 文本在折叠态隐藏时，必须同时使用 `opacity-0` 和 `w-0`。
- 如果 dropdown 可能受 overflow 裁剪影响，应优先使用 `<Teleport to="body">`。
- 优先采用 production-grade 方案，不做随意的临时拼接式实现。
- 这个 context 文件应该保持紧凑，服务于 AI 快速读取，而不是承担完整项目历史归档。

## 维护规则
- 这个文件只保留当前仍然有效的项目状态。
- 更新时优先重写摘要，不要机械地无限追加内容。
- `最近迭代` 只保留最近 8 次以内的记录。
- 旧的迭代信息应压缩进 `历史摘要`，不要让全文持续变长。
- 如果某次改动不足以影响项目理解，就不要把噪音写进来。

## 最近迭代
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
