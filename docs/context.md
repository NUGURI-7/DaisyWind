# DaisyWind Context

## 项目概述
- DaisyWind 是一个个人独立开发的 full-stack 项目，前端使用 Vue 3，后端使用 FastAPI。
- 当前定位：聚焦 AI 核心能力的技术验证平台，优先实现 Pydantic AI Agent 对话系统、RAG 知识库检索、以及对话相关的前后端基础设施。
- 已有基础设施：认证系统、可折叠 Sidebar 布局、Notes 模块（基础版已完成，后续增强暂缓）。
- 这个文件是后续 AI 新对话的单一项目上下文来源。

## 早期方向参考（低权重）
- 这部分只用于提供产品方向上的大致印象，帮助 AI 理解项目可能的长期演化方向。
- 这不是正式需求，不构成强约束，也不代表相关能力已经实现。
- 如果与当前代码现状、你在当次对话中的明确要求或后续决策冲突，应以实际项目状态和当前任务为准。
- **当前阶段收窄**：从"通用 AI 助手平台"收缩为"AI 核心能力技术验证平台"。Notes 系统、复杂前端交互等非 AI 核心功能已暂缓，前端仅做满足测试和验证需要的最小实现。
- 目前可以暂时将 DaisyWind 理解为一个面向个人使用场景的智能 AI Agent 助手项目。
- 它的整体方向不是停留在传统的一问一答式对话工具上，而是希望逐步演化为一个更具主动性、可调用工具、可协助处理任务，并能够沉淀用户有效信息的个人智能助手。
- 当前这段描述主要用于提供产品方向上的粗略印象，不应视为固定产品定义；后续产品形态、能力边界和知识沉淀方式仍可能随着开发持续调整。

## 技术栈
- Frontend: Vue 3, Vite, TypeScript, Pinia, Vue Router, Tailwind CSS v4, shadcn-vue (Reka UI v2), `@phosphor-icons/vue`
- Frontend editor: Milkdown Crepe
- Backend: FastAPI, Tortoise ORM, Redis, PostgreSQL, JWT auth
- Python tooling: `uv`, Tortoise ORM 内置迁移（`tortoise` CLI）
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
- Notes 模块（P1 已完成，后续增强暂缓——当前阶段聚焦 AI 核心能力）：`api/note.ts` + `stores/notes.ts`（Pinia，autosave debounce + race condition 保护）+ `views/notes/index.vue`（接入 API，可折叠列表面板，AI 面板 toolbar 切换，删除确认）。Milkdown Crepe editor 含代码块折叠/复制反馈、block hover 背景高亮。
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

## 已完成：Chat 模块 P0（2026-04-17，M1 里程碑达成）
- **Provider 工厂**：`backend/app/agents/providers.py` 基于 PydanticAI 新 API（Model + Provider 分离），当前支持 DeepSeek 和 Gemini，配置驱动。
- **Chat Agent**：`backend/app/agents/chat_agent.py` + `deps.py`，最小 system prompt + `AgentDeps` 运行时容器（user、conversation）。
- **SSE 结构化事件协议**：`/api/nuguri/v1/chat/send`，事件类型含 `message_start` / `content_block_start|delta|stop` / `message_delta` / `message_stop` / `error`，P1 加 Tool 时可直接增量扩展。
- **对话持久化 + CRUD**：`Conversation`（含 `provider` / `model` / `summary` / `cost`）+ `ChatMessage`，`get_or_create_conversation` 惰性创建，list/detail/delete 接口。
- **前端 Chat UI**：Pinia store 驱动的事件级块状态机、fetch-based SSE 消费（非 EventSource）、Sidebar 内嵌 `Recents` 对话列表、URL 同步 `/chat/:uuid?`、切换/新建/删除完整闭环。
- **关键细节**：`Conversation.model_str` 重命名为 `Conversation.model`（Pydantic v2 对 `model` 字段名无警告）；高度链用 `min-h-0` + `shrink-0` 解决 flex 输入框贴底问题；`get_conversation_or_404` 补齐 `return`。

## 其他进行中
- Settings 入口已接入 ThemeSwitcher（Popover 弹出，含 12 主题色 + Light/Dark 切换）。

## 下一步
- **当前重点**：进入 Chat P1 — Tool 调用与多 Agent（`@agent.tool` 工具系统、Orchestrator 模式、Web 搜索 Tool、Notes 搜索 Tool、前端 Tool 调用卡片渲染）。
- **后续方向**：P2（RAG 知识库检索，pgvector + Embedding）。详见 `docs/roadmap.md`。
- **流式渲染规范**：SSE 事件协议、前端块级状态机、组件映射。详见 `docs/streaming-render.md`。

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
### 2026-04-17（Chat 模块 P0 完成，M1 里程碑达成）
- 后端完成 Provider 工厂 + PydanticAI Agent + SSE 结构化流式接口 + 对话 CRUD 持久化。详见本文档上方「已完成：Chat 模块 P0」小节。
- 前端完成 Pinia 事件驱动状态机 + fetch SSE 消费器 + Sidebar 内嵌 `Recents` 列表 + URL 路由同步。
- 字段重命名：`Conversation.model_str` → `Conversation.model`，用 Tortoise `RenameField` 迁移，无数据丢失。
- 修复多处：输入框未贴底的 flex 高度链问题（`min-h-0` + `shrink-0`）、`get_conversation_or_404` 漏 `return`、`ConversationOut` 缺 `ConfigDict(from_attributes=True)`。
- P0 范围决议（不做空状态 Landing Page / 不做流式取消 / 不做 Starred 分组 / 不做"⋯"菜单 / 不做模型选择器）全部兑现，这些条目已归入 `roadmap.md` 的 Phase 2 体验增强。

### 2026-03-17（UI 细节优化、API 调整与前端图片直传接入）
- 前端图片上传接入：修复了 `api/media.ts` 中 `getPresignedUrl` 的参数拼写错误，并在 Notes 的 Milkdown (Crepe) 编辑器中全面接入图片直传 OSS (R2) 逻辑（覆盖 ImageBlock、拖拽及粘贴上传），上传成功后自动替换为公共访问链接。
- Sidebar 动画重构：改用 Tailwind 原生的 `max-w-[200px]`、`opacity-0` 和 `transition-all` 组合，实现更平滑的文本和图标展开/折叠动画。
- Milkdown 代码块 UI 深度定制：在 `app.css` 中注入了一套抗锯齿和覆盖默认边框、背景、行号的样式，使代码块呈现更纯净的 Claude 风格（无色差浅灰/深灰背景，优化顶部工具栏和语言选择器）；同时优化了 CodeMirror 语法高亮样式排版。
- Editor 键盘交互增强：在 Notes 编辑器中增加了语言选择器的键盘导航（`ArrowUp`、`ArrowDown`、`Enter`）支持。
- API 规范化：将后端的 `/current_user` 路由和前端调用统一修改为 `/current-user`；移除了后端未使用的 `play.router`。

### 2026-03-14（R2 对象存储前端直传方案：后端完成）
- 引入了 `boto3` SDK，对接 Cloudflare R2（S3 兼容）对象存储。
- 放弃了本地存图和 Cookie 鉴权的方案，改为更高级的“前端直传 (Presigned URL)”模式。
- 新增 `R2Storage` 工具类和 `POST /api/nuguri/v1/media/presigned-url` 接口，后端不再落盘文件，仅颁发具有 5 分钟有效期的 PUT 签名。
- 增强了文件上传的安全校验，拒绝无后缀名文件，统一使用 UUID 生成文件名。
- 解决了 Cookie CSRF 和静态资源跨域访问鉴权的问题。

### 2026-03-13（主题系统：12 主题色 + Light/Dark 切换）
- 新增 `composables/useTheme.ts`：管理主题状态（theme name + dark mode），localStorage 持久化。
- 新增 `components/ThemeSwitcher.vue`：色块网格 + Light/Dark 切换面板。
- `app.css` 新增 11 套主题变量（Neutral/Zinc/Gray/Slate + Rose/Red/Orange/Green/Blue/Yellow/Violet），每套含 light + dark。
- Sidebar Settings 按钮接入 shadcn-vue Popover，弹出 ThemeSwitcher。

### 2026-03-12（全量迁移至 shadcn-vue 体系完成）
- 彻底卸载 daisyUI，使用 shadcn-vue（Reka UI v2）和原生 Tailwind v4 接管全局样式。
- 确立了 11 套暖色调 CSS 变量系统（`docs/design-tokens.md`）。
- Login、Register、Notes、Chat 和 Sidebar (Flexbox + data-[collapsed] 原生重构) 已全量重构完成。

### 2026-03-10（Notes UI 深度打磨与 Bug 修复）
- 移除了全局的 `btn-ghost` 依赖，改用纯 Tailwind v4 工具类构建精致 hover。
- 优化了 Notes 列表交互（左侧高亮指示线，Hover 微移，时间重排）。
- 引入 URL 驱动状态，通过 `vue-router` 将 `selectedId` 绑定至 URL query，解决刷新和路由切换时的状态丢失问题。
- 重绘了无笔记选中时的右侧引导空状态（Empty State）组件。

## 历史摘要
- 早期 backend 基础已经具备 FastAPI app 启动、Redis/PostgreSQL 生命周期接入、Tortoise ORM 模型和 auth 相关服务。
- frontend 基础已经具备 login/register 流程、主布局、可折叠 sidebar 以及 notes editor 页面。
- Notes 后端 CRUD 接口（列表、新建、详情、更新、软删除）已就绪，并在第一阶段实现了带防抖自动保存的前端交互。
- 登录流程同步收集 `last_login` 和 `login_count`，为数据分析打下基础。

## 后续使用方式
- 每次开启新的 AI 对话时，先读取这个文件。
- 每次完成有意义的开发后，更新这个文件一次。
- 可以直接用类似 `更新 context`、`把这次改动写入 context`、`压缩 context` 的指令触发维护。
