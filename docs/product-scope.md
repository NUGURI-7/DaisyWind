# Windify — Product Scope

> 本文档定义 Windify 当前阶段的产品范围、技术栈和架构方向。
> 最后更新：2026-03-25

---

## 1. 产品定位

**Windify 是一个聚焦 AI 核心能力的技术验证平台。**

当前阶段的目标不是构建一个完整的消费级产品，而是从零实现一个现代 AI Agent 系统的核心能力栈，包括：

- 基于 PydanticAI 的 Agent 对话系统（多模型、Tool 调用、多 Agent 协作）
- RAG 知识库检索（Embedding → 向量存储 → 语义搜索）
- 对话相关的前后端基础设施（SSE 流式输出、对话持久化、最小可用前端）

这是一个**学习驱动**的项目：通过端到端实现来理解现代 Agent 系统的设计模式和工程实践。

---

## 2. 当前阶段做什么

### 核心能力（必须实现）

| 能力 | 说明 |
|------|------|
| **多 Provider 模型调用** | 通过 PydanticAI 原生支持 DeepSeek / OpenAI / Claude / Gemini / Qwen，统一 Provider 管理 |
| **基础 Agent 对话** | PydanticAI Agent + 依赖注入（`RunContext[Deps]`），支持流式响应 |
| **SSE 流式输出** | FastAPI StreamingResponse，Claude 风格的结构化 SSE 事件协议 |
| **对话持久化** | Conversation + ChatMessage CRUD，历史消息加载 |
| **Tool 调用系统** | Agent 自主决定调用工具（`@agent.tool`），前端展示 Tool 调用过程 |
| **多 Agent 协作** | Orchestrator 意图判断 + 委派专项 Agent（Research / Web / Code） |
| **Web 搜索 Tool** | Tavily API 接入，Agent 能联网检索 |
| **Notes 搜索 Tool** | Agent 能搜索用户已有的 Notes 内容 |
| **RAG 语义检索** | Embedding 抽象层 + pgvector 向量存储 + Notes 索引器 + RAG Tool |

### 前端（最小实现）

前端在当前阶段只做满足测试和验证需要的最小实现：

- Chat 消息列表 + 输入框 + SSE 流式渲染
- Tool 调用过程的可视化卡片
- 对话列表管理（创建 / 切换 / 删除）
- 模型选择器

不追求精致的交互体验和动画细节，能用、能测试即可。

---

## 3. 当前阶段不做什么

以下功能不属于当前阶段重点，但保留在规划中，待核心能力跑通后再评估：

| 功能 | 状态 | 说明 |
|------|------|------|
| Notes 模块增强 | ⏸️ 暂缓 | 基础 CRUD + Milkdown 编辑器已完成，图片上传等增强暂停 |
| 多模态消息（图片输入） | ⏸️ 暂缓 | 架构已设计（JSON 多段结构），实现推迟 |
| Context 自动摘要压缩 | ⏸️ 暂缓 | 长对话 token 超限时的自动压缩 |
| Token 计费统计 UI | ⏸️ 暂缓 | 后端计费逻辑可随 P0 顺带实现，UI 推迟 |
| 代码执行沙箱 | ⏸️ 暂缓 | Docker/Firecracker 外置沙箱，复杂度高 |
| 复杂前端交互 | ⏸️ 暂缓 | 对话分支、拖拽、精致动画等 |
| 用户级限流 | ⏸️ 暂缓 | 个人项目暂不需要 |
| 对话标题自动生成 | ⏸️ 暂缓 | 现有逻辑取前 30 字够用 |

---

## 4. 核心技术栈

### 后端

| 层 | 技术 | 用途 |
|----|------|------|
| Web 框架 | FastAPI | API 路由、SSE 流式响应 |
| Agent 框架 | PydanticAI | Agent 编排、Tool 定义、依赖注入、多 Provider 支持 |
| ORM | Tortoise ORM + Aerich | 数据模型、迁移 |
| 数据库 | PostgreSQL + pgvector | 业务数据 + 向量存储 |
| 缓存/队列 | Redis + ARQ | 会话状态、异步任务（Notes 索引） |
| 联网搜索 | Tavily | Agent Web 搜索 Tool |
| 对象存储 | Cloudflare R2 | 图片等媒体文件（已有） |

### 前端

| 层 | 技术 | 用途 |
|----|------|------|
| 框架 | Vue 3 + Vite + TypeScript | SPA |
| 状态管理 | Pinia | 全局状态 |
| UI 组件 | shadcn-vue (Reka UI v2) | 组件库 |
| 样式 | Tailwind CSS v4 | 工具类 CSS |
| 图标 | @phosphor-icons/vue | 统一图标 |
| 编辑器 | Milkdown Crepe | Notes 富文本（已有，暂缓增强） |

---

## 5. 架构方向

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Vue 3)                  │
│  Chat UI ←── SSE ──→ FastAPI StreamingResponse      │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│                  FastAPI Backend                      │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │           Orchestrator Agent                 │    │
│  │  (PydanticAI + RunContext[AgentDeps])        │    │
│  │                                              │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │    │
│  │  │ Research  │ │   Web    │ │   Code   │    │    │
│  │  │  Agent    │ │  Agent   │ │  Agent   │    │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘    │    │
│  │       │             │             │          │    │
│  │  ┌────▼───┐   ┌────▼────┐  ┌────▼────┐    │    │
│  │  │RAG Tool│   │ Tavily  │  │Sandbox  │    │    │
│  │  │Notes   │   │ Search  │  │(⏸️ 暂缓) │    │    │
│  │  │Tool    │   │         │  │         │    │    │
│  │  └────┬───┘   └─────────┘  └─────────┘    │    │
│  └───────┼──────────────────────────────────────┘    │
│          │                                           │
│  ┌───────▼───────────────────────────────────┐      │
│  │  PostgreSQL (pgvector) │ Redis │ R2       │      │
│  └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **PydanticAI 为中心**：所有 Agent 逻辑通过 PydanticAI 编排，利用其依赖注入和类型安全特性
2. **单体部署**：不引入微服务、Proxy 进程或独立 Worker，所有组件跑在一个 FastAPI 进程内（ARQ 除外）
3. **复用已有基础设施**：PostgreSQL（+ pgvector）、Redis、R2 均已接入，不引入新的基础设施依赖
4. **前端最小化**：当前阶段前端只做功能验证，不投入设计打磨

---

## 维护规则

- 产品定位或范围发生变化时，更新本文档
- "不做什么"列表中的条目恢复为活跃状态时，移到"做什么"并更新 `docs/roadmap.md`
