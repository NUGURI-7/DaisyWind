# Windify — Development Roadmap

> 基于 AI 核心能力技术验证的阶段性路线图。
> 最后更新：2026-04-17

---

## Phase 1：AI 核心能力（当前阶段）

目标：从零跑通一个完整的现代 AI Agent 系统。

### P0 — 端到端对话（最高优先级）✅ 已完成 2026-04-17

完成后得到：一个能选模型、能流式对话、能保存历史的基础聊天应用。

| # | 任务 | 说明 | 依赖 |
|---|------|------|------|
| 1 | Provider 管理 | `agents/providers.py`：根据配置创建 PydanticAI Model 实例，支持 DeepSeek / OpenAI / Claude / Gemini / Qwen | 无 |
| 2 | 基础 Agent | 用 PydanticAI 创建最简 Agent（无 Tool），验证框架跑通 | #1 |
| 3 | SSE 流式接口 | FastAPI `StreamingResponse` + `agent.run_stream()`，**从 P0 起就使用结构化 SSE 事件协议**（message_start / content_block_delta / message_stop），P1 加 Tool 时只需增量添加新事件类型，无需重构 | #2 |
| 4 | 对话持久化 | Conversation + ChatMessage 模型扩展 + CRUD 接口 | #2 |
| 5 | 前端最小 Chat UI | 消息列表 + 输入框 + SSE 消费 + 事件级块渲染（详见 `docs/streaming-render.md`） | #3, #4 |

> P0 范围决议（做/不做清单）已兑现，详见 `docs/context.md` 的 2026-04-17 迭代记录；延后项均已挂入 Phase 2。

### P1 — Tool 调用与多 Agent

完成后得到：一个能联网搜索、能查笔记的 AI 助手，具备 Agent 核心差异化能力。

| # | 任务 | 说明 | 依赖 |
|---|------|------|------|
| 6 | Tool 系统 | `@agent.tool` 定义工具，Agent 自主决定调用时机 | P0 |
| 7 | Orchestrator 模式 | 主 Agent 意图判断 + 委派专项 Agent | #6 |
| 8 | Web 搜索 Tool | Tavily API 接入，Agent 能联网查资料 | #6 |
| 9 | Notes 搜索 Tool | Agent 搜索用户已有的 Notes 内容（全文搜索） | #6 |
| 10 | 前端 Tool 展示 | SSE 事件中渲染 Tool 调用卡片（"正在搜索…"等） | #6, P0#5 |

### P2 — RAG 知识库检索

完成后得到：Agent 能根据语义理解检索知识库，从"关键词搜索"升级为"语义理解"。

| # | 任务 | 说明 | 依赖 |
|---|------|------|------|
| 11 | Embedding 抽象层 | `EmbeddingProvider` 基类 + 至少一个实现（Qwen / OpenAI） | 无 |
| 12 | pgvector 向量存储 | PostgreSQL pgvector 扩展，NoteEmbedding 模型，向量读写 | #11 |
| 13 | Notes 索引器 | Note 创建/更新时异步分块 → Embedding → 写入 pgvector（ARQ） | #12 |
| 14 | RAG Tool | Agent 调用时做向量相似度搜索，返回最相关笔记片段 | #13, P1 |

---

## Phase 2：体验增强（待定）

> ⏸️ 以下功能待 Phase 1 核心能力跑通后再评估优先级和实施顺序。

| 功能 | 说明 | 对应架构文档 |
|------|------|-------------|
| Chat 空状态 Landing Page | 新对话时显示居中问候语 + 建议 prompt 卡片（Claude 风格），输入框居中而非贴底 | — |
| Chat 侧栏精致化 | ConversationList 加 Starred/Pinned 分组、hover "⋯" 三点菜单替换直接删除按钮、Recents "View all" 或分页 | — |
| 多模态消息 | 图片输入，ChatMessage.content 改为 JSON 多段结构 | chat-architecture.md §4.5 |
| Context 自动摘要 | 长对话 token 超限时，用 LLM 压缩早期消息 | chat-architecture.md §4.4 |
| 用户取消生成 | Redis flag + SSE 循环检查，前端"停止"按钮 | chat-architecture.md §4.7 |
| Token 计费统计 UI | 聚合用量数据，展示费用统计面板 | chat-architecture.md §4.10 |

---

## Phase 3：能力扩展（待定）

> ⏸️ 长期方向，不构成当前约束。

| 功能 | 说明 |
|------|------|
| 代码执行沙箱 | Docker / Firecracker 外置沙箱，Agent 能写代码并安全执行 |
| Notes 模块增强 | 图片上传增强、协作编辑、版本历史等 |
| 复杂前端交互 | 对话分支（edit & branch）、精致 UI 动画 |
| 对话标题自动生成 | AI 根据对话内容生成标题 |
| 用户级限流 | API 调用频率限制 |

---

## 里程碑检查点

| 检查点 | 标志 | 意义 |
|--------|------|------|
| **M1** ✅ | P0 完成（2026-04-17） | 端到端 AI 对话跑通，能选模型、能流式输出、能保存历史 |
| **M2** | P1 完成 | Agent 能调用工具，具备联网搜索和笔记检索能力 |
| **M3** | P2 完成 | RAG 语义检索就绪，Agent 能理解并检索私有知识库 |
| **M4** | Phase 1 收尾 | 核心 AI 能力验证完成，评估是否进入 Phase 2 |

---

## 维护规则

- 完成一个 P 阶段后，更新本文档标注完成日期
- Phase 2/3 的条目恢复为活跃时，移到 Phase 1 并细化任务拆分
- 同步更新 `docs/context.md` 和 `docs/product-scope.md`
