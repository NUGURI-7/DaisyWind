# Conversation Ingestion — 架构设计文档

> 把对话（DaisyWind 内部 / 外部分享链接 / 粘贴文本）通过多 Agent 编排整理成结构化 Note。
> 同时为后续 RAG 知识库提供高质量语料来源。
> 最后更新：2026-04-22

---

## 一、目标与定位

### 1.1 业务目标

- **整理零散对话**：把跨平台、跨会话的对话内容沉淀为可检索的笔记
- **AI 资源沉淀**：为后续 Phase 1 P2（RAG 知识库）准备高质量结构化语料
- **验证多 Agent 编排能力**：作为 DaisyWind AI 核心能力技术验证的关键场景

### 1.2 设计定位

本模块**不是流水线（Pipeline）**，而是**真正的多 Agent 编排（Orchestration）**。

| 维度 | Pipeline（不采用） | Orchestration（本模块） |
|---|---|---|
| 控制流 | 代码写死 A→B→C | LLM 推理动态决定下一步 |
| 步骤数 | 固定 | 可增可减、可循环、可分支 |
| 子任务 | 串行 | 可 fan-out 并行 |
| 状态 | 函数返回值传递 | Blackboard 共享 |
| 失败处理 | 重试当前步 | Orchestrator 重新规划 |

理由：一段闲聊和一段技术深聊该走的路完全不同（要不要拆多篇？要不要补外部资料？要不要合并到已有 Note？），写死流程会很别扭。

### 1.3 核心原则

**架构 day-1 即完全体；首版只是"少注册几块组件"。**

新增能力（新 Source / 新 Worker / Logfire / 并行）= 纯增量文件 + registry 注册一行，**不动核心代码、不改 DB schema、不改事件协议**。
不存在"MVP 重写"，只有"功能逐步 enable"。

---

## 二、编排范式

**`Orchestrator-Worker` 为主骨架，嵌套一个 `Reflection Loop` 做质量控制。**

```
        ┌──────────────────────────────┐
        │      Orchestrator Agent      │
        │  (Planner + Decision Maker)  │
        └──┬────────────┬────────────┬─┘
           │ tool call  │ tool call  │ tool call
           ▼            ▼            ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │Classifier│  │ Outliner │  │ Searcher │  ...workers
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         │             │             │
         └──── patch ──┴──── patch ──┘
                       ▼
              ┌─────────────────┐
              │   Blackboard    │  (PG JSONB)
              │ (Shared State)  │
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Critic Agent   │ ←─┐
              │  (评审 + 打分)   │   │ reflection
              └────────┬────────┘   │
                       │ 不通过      │
                       └────────────┘
                       │ 通过
                       ▼
                 ┌──────────┐
                 │ Finalize │ → 写入 Note
                 └──────────┘
```

为什么不用其他范式：

- **Plan-and-Execute**：对话整理的"计划"本身就是任务的一部分，不该提前固化
- **Handoff / Routing**：需要全局视野（合并 Note、整体结构），中央调度更合适
- **Multi-Agent Debate**：写作类任务用不到多视角辩论

为什么不用 LangGraph / pydantic-graph：

- 编排是"LLM 主导决策" + "tool calling loop"，PydanticAI 原生 `agent.run` 已经提供循环和工具调用
- pydantic-graph 适合**节点关系是程序员设计的状态机**（条件转移、并行 join 由代码定义）
- 我们这套是 LLM 自己规划路径，graph 反而碍事

---

## 三、完全体能力清单 vs 首版交付

| 类别 | 完全体 | 首版交付 |
|---|---|---|
| **输入源** | DaisyWind 内部对话 | ✅ |
| | DeepSeek 分享链接 | ✅ |
| | 粘贴文本 | ✅ |
| | ChatGPT / Claude / Kimi 分享 | 📦 |
| **Worker** | Classifier / Outliner / Writer / Critic | ✅ |
| | Searcher（查 Notes / 联网） | 📦 |
| | Linker（关联已有 Note） | 📦 |
| | Tagger | 📦 |
| **编排能力** | Orchestrator 动态决策（tool calling loop） | ✅ |
| | Reflection 回炉 | ✅ |
| | 大纲人确认（await_user） | ✅ |
| | 失败/中断断点续跑 | ✅ |
| | 一段对话拆多篇 Note | 📦 |
| | SectionWriter 并行 fan-out | 📦 |
| **可观察** | SSE 事件流 + 决策可视化 | ✅ |
| | Logfire trace | 📦 |
| **模型分级** | 每个 Worker 独立 provider+model | ✅ |

📦 = 架构已支持，首版不实例化（不写文件 / 写了不 register）。新增时纯增量。

---

## 四、核心架构

### 4.1 数据模型

```
IngestionRun                       — 一次 ingestion 任务
  - id, user_id
  - source_type, source_ref         — internal / deepseek_share / pasted
  - status                          — pending|running|awaiting_user|succeeded|failed|cancelled
  - blackboard: JSONB               — 全部中间状态
  - created_at, updated_at, completed_at

IngestionEvent (append-only)        — 完整执行 trace，可重放
  - id, run_id, ts
  - actor                           — orchestrator|<worker_name>|user|system
  - kind                            — decision|tool_call|tool_result|state_patch|await_user|user_resume|error
  - payload: JSONB
```

**Run 持久 + Event 可重放** = 断点续跑、调试、Logfire 后续替换都白送。

### 4.2 三个抽象基类（架构骨干，永不变）

```
SourceAdapter      .match(uri)         -> bool
                   .fetch(uri)         -> RawConversation

Worker             .name / .model
                   .run(state)         -> patch (dict)

Orchestrator       PydanticAI Agent + 一组 Worker-as-tool
```

**新增能力 = 新增子类 + register**，三个基类签名永不变。

### 4.3 Orchestrator 主循环

```
loop:
  state = load_blackboard(run_id)
  decision = orchestrator_agent.run(state, history)   # LLM 决策
  if decision.tool == "finalize":   commit & break
  if decision.tool == "await_user": status=awaiting_user; break
  result = workers[decision.tool].run(decision.args, state)
  patch_blackboard(result)
  emit_events(...)
```

这就是"真编排"——每轮 LLM 看状态决定下一步，不是写死的 DAG。
恢复执行 = 用户 resume 后重新进入这个 loop，Orchestrator 看到新 state 自然续。

### 4.4 Worker = PydanticAI Agent 包装

每个 Worker 内部是独立的小 Agent（自己的 system prompt + model），对外暴露为 Orchestrator 的一个 tool。

优势：
- 每个 Worker 单测、独立换模型
- Searcher / Linker 这种内部还要调 tool 的 Worker，用 PydanticAI "agent-as-tool" 模式自然嵌套
- 模型可被前端配置覆盖

### 4.5 Blackboard

存 Run 的 `blackboard` JSONB 字段。Pydantic 模型用 `extra="allow"`，新字段不破坏老 run。Worker 只输出 patch（dict），由 state 层合并，避免并发覆盖。

```
IngestionState {
  raw_conversation: [...]
  classification: {...}
  outline: {...}
  sections: {idx: content}
  critic_feedback: [...]
  related_notes: [...]
  decisions_log: [...]
}
```

### 4.6 人在回路（await_user）

`await_user_input(stage, payload)` 是 Orchestrator 的一个 tool。

```
Orchestrator decides await_user
  → run.status = awaiting_user
  → emit await_user event
  → loop break
                                       ↓
前端 SSE 收到 await_user → 渲染对应 stage 的交互 UI
                                       ↓
用户提交 → POST /ingest/runs/{id}/resume → 写 user_resume event
                                       ↓
重新触发 loop → Orchestrator 看到新 state 继续
```

**任何阶段都能 await_user**，不只是大纲。完全体里 Critic 不通过、Linker 拿不准都可以问。
首版仅在 Outline 阶段触发。

### 4.7 SSE 事件协议

沿用 Chat 模块的设计哲学（`actor + kind + payload` 三件套）：

```
- run_started
- orchestrator_decision   { tool, args, reasoning, model }
- worker_started          { worker, input }
- worker_streaming        { worker, delta }     # Writer 流式
- worker_completed        { worker, output, duration, tokens }
- state_patched           { patch }
- await_user              { stage, payload }
- critic_feedback         { score, issues }
- run_completed           { note_id }
- run_failed              { error }
```

前端能据此做出 Claude Code 风格的 trace 面板。

### 4.8 异步执行 — ARQ

**ARQ** = Async Redis Queue，原生 asyncio 后台任务队列，复用项目已有 Redis。

为什么必须从 day-1 就用：
- 一次 ingestion 可能跑 30s ~ 几分钟（多次 LLM 调用）
- HTTP 请求挂这么久不可接受
- 标准做法：HTTP 创建 run → 丢任务到队列 → worker 进程异步执行 → 前端 SSE 订阅进度
- 先同步再迁 = 破坏性升级，违背"完全体架构 day-1"原则

替代方案对比：
- Celery：重，sync 起家，async 支持差
- FastAPI BackgroundTasks：同进程跑，崩了就丢，不能扩进程，不算 production-grade
- ARQ：轻量、原生 async、复用 Redis ✅

---

## 五、文件结构

```
backend/app/ingestion/
  models.py            IngestionRun / IngestionEvent
  schemas.py           Blackboard / RawConversation / events
  state.py             Blackboard 读写 + patch 合并
  events.py            事件 emit + SSE 序列化（Logfire hook 留点）

  sources/
    base.py            SourceAdapter ABC + registry
    internal.py
    deepseek_share.py
    pasted.py
    # chatgpt.py / claude.py / kimi.py 后续添加

  workers/
    base.py            Worker ABC + agent 包装
    registry.py        worker 注册表
    classifier.py
    outliner.py
    writer.py
    critic.py
    # searcher.py / linker.py / tagger.py 后续添加

  orchestrator.py      Orchestrator agent + 主循环
  runner.py            ARQ job entry
  api.py               start / get / sse / resume / cancel

frontend/src/
  views/notes/
    # ingestion 入口与列表挂在 Notes 模块内
  components/notes/ingestion/
    IngestEntry.vue       — 触发入口（粘 URL / 选会话 / 粘文本）
    IngestRunPanel.vue    — 运行面板（trace + blackboard + await_user）
    TraceTimeline.vue
    OutlineReview.vue     — 大纲确认 UI
    BlackboardView.vue
  stores/ingest.ts
  api/ingest.ts
```

---

## 六、模型配置策略

### 6.1 默认配置（首版）

**全部 Worker 默认使用 `deepseek-chat`**，省事 + 成本低。

| Worker | 默认 model | 备注 |
|---|---|---|
| Orchestrator | deepseek-chat | 决策不需要顶级模型 |
| Classifier | deepseek-chat | |
| Outliner | deepseek-chat | |
| Writer | deepseek-chat | |
| Critic | deepseek-chat | 必须独立于 Writer，避免 self-bias |

### 6.2 可配置性

- 每个 Worker 的 `provider + model` 可被**前端运行时覆盖**
- 配置参数通过 ingestion 启动接口传入，Orchestrator 透传给对应 Worker
- 用户可在新建 ingestion 时自由组合各 Worker 的模型（比如 Writer 单独用 Gemini Pro）

### 6.3 完全体扩展

后续可引入"模型分级 preset"（fast / balanced / premium），一键切换全部 Worker 配置组合。

---

## 七、输入源策略

### 7.1 DeepSeek 分享链接

通过 `httpx` 直接调用 DeepSeek 的非公开 API（已验证可行）：

```
GET https://chat.deepseek.com/api/v0/share/content?share_id={SHARE_ID}
```

返回完整结构化 JSON（`title` / `messages[]` / `fragments[]` / `inserted_at` / 等），**无需 headless 浏览器、无需爬虫**。

合规说明：分享链接的诞生意味着内容已被用户主动 public，访问公开分享内容不构成侵权。

### 7.2 内部对话

直接读 DB（`Conversation` + `ChatMessage`），转换为统一的 `RawConversation` 格式。

### 7.3 粘贴文本

兜底方案，用户粘任意 Markdown / 纯文本，由 Classifier 判断是否可识别为对话结构。

### 7.4 后续扩展

每加一个平台 = 新增一个 `SourceAdapter` 子类 + registry 注册，不动核心。

---

## 八、前端入口决议

**ingestion 功能不在 Sidebar 加新模式，全部挂在 Notes 模块内。**

- **触发入口**：Notes 模块内的"从对话生成"按钮（具体位置 toolbar / 列表上方 / 编辑页内待定）
- **运行状态追踪**：进行中的 ingestion runs 列表也在 Notes 模块内展示
- **完成产物**：自动落入 Notes 列表，与普通 Note 等同

---

## 九、已决议事项汇总

| # | 决议 | 时间 |
|---|------|------|
| 1 | 编排范式：Orchestrator-Worker + Reflection Loop | 2026-04-22 |
| 2 | 编排框架：PydanticAI 自建，不引入 LangGraph | 2026-04-22 |
| 3 | Logfire 后期接入，不影响首版 | 2026-04-22 |
| 4 | 大纲阶段触发 await_user 人确认 | 2026-04-22 |
| 5 | 不做 MVP，架构 day-1 即完全体，首版只是少注册组件 | 2026-04-22 |
| 6 | 接受 DeepSeek 分享链接的"自分享自抓"灰区 | 2026-04-22 |
| 7 | Worker 默认全部 deepseek-chat，前端可覆盖 | 2026-04-22 |
| 8 | 入口与运行追踪挂在 Notes 模块内 | 2026-04-22 |
| 9 | 异步执行用 ARQ，复用现有 Redis | 2026-04-22 |

---

## 十、待定事项

- DB 表 `IngestionRun` / `IngestionEvent` 的 Tortoise model 与迁移落地方案确认
- ARQ 依赖引入与 worker 进程启动方式确认
- Notes 模块内 ingestion 入口的具体位置（toolbar / 列表 / 编辑页）
- Orchestrator system prompt 详细设计（tool 列表说明、决策 heuristic）
- 各 Worker 的 system prompt 详细设计
- 前端 trace 面板的视觉规范

---

## 十一、与 RAG（P2）的衔接

本模块产出的 Note 天然是高质量 RAG 语料：

- 已被 Critic 评审过质量
- 已被 Outliner 结构化（标题 / 章节）
- 已被 Tagger 打标签（完全体）
- 已被 Linker 关联到已有知识网络（完全体）

P2 启动时，RAG 索引器只需订阅"Note 写入"事件即可自动入库。
