# Conversation Ingestion — 架构设计文档

> 把对话（DaisyWind 内部 / 外部分享链接 / 粘贴文本）通过多 Agent 编排整理成结构化 Note。
> 同时为后续 RAG 知识库提供高质量语料来源。
> 最后更新：2026-04-23

---

## 一、目标与定位

### 1.1 业务目标

- **整理零散对话**：把跨平台、跨会话的对话内容沉淀为可检索的笔记
- **AI 资源沉淀**：为后续 Phase 1 P2（RAG 知识库）准备高质量结构化语料
- **验证多 Agent 编排能力**：作为 DaisyWind AI 核心能力技术验证的关键场景

### 1.2 设计定位

本模块**不是流水线（Pipeline）**，而是**真正的多 Agent 编排（Orchestration）**。

| 维度 | Pipeline | Orchestration |
|---|---|---|
| 控制流 | 代码写死 A→B→C | 显式图驱动，节点可分支/回环 |
| 步骤数 | 固定 | 可增可减、可循环 |
| 状态 | 函数返回值传递 | Blackboard 共享 |
| 失败处理 | 重试当前步 | 节点状态机决定 |

理由：一段闲聊和一段技术深聊该走的路完全不同（要不要拆多篇？要不要补外部资料？要不要合并到已有 Note？），写死流程会很别扭。

### 1.3 核心原则

**架构 day-1 即完全体；首版只是"少注册几块组件、少做几块前端 UI"。**

- 新增能力（新 Source / 新 Node 类型 / Logfire / 并行 / 拖拽编辑器）= 纯增量
- 不动核心代码、不改 DB schema、不改事件协议
- 不存在"MVP 重写"，只有"功能逐步 enable"

---

## 二、编排范式：Graph + Agent-in-Node 混合架构

### 2.1 整体形态

```
┌─────────────────────────────────────────────────┐
│            Graph Engine (外层骨架)               │
│  ┌──────┐  ┌──────────┐  ┌──────┐  ┌────────┐  │
│  │Source│→ │Classifier│→ │Outlin│→ │ Human  │  │
│  └──────┘  └──────────┘  │  er  │  │ Review │  │
│                           └──────┘  └────┬───┘  │
│                                          ▼      │
│              ┌──────────┐         ┌────────┐   │
│              │  Critic  │  ←──    │ Writer │   │
│              └─────┬────┘  fail   └────────┘   │
│                    │ pass     ▲                 │
│                    ▼          │ back-edge       │
│              ┌──────────┐     │ (max 3 iter)    │
│              │   Sink   │     │                 │
│              └──────────┘     └─────────────────┘
└─────────────────────────────────────────────────┘
                  ↑
       前端 Vue Flow 渲染图，节点状态实时高亮
       首版只读，后续可拖拽编辑
```

**外层是图（用户看得见、可干预），内层节点可以是 Agent（保留智能）。**

### 2.2 范式选型对比

| 范式 | 适合度 | 备注 |
|---|---|---|
| Pure Agent Loop（LLM 主导） | ❌ | 用户控制感弱，不可视化 |
| Pure Pipeline | ❌ | 写死流程不灵活 |
| **Graph + Agent-in-Node** | ✅ | 业界共识方案 |
| Plan-and-Execute | ❌ | 计划本身就是任务的一部分 |
| Handoff / Routing | ❌ | 缺乏全局视野 |

### 2.3 框架选型：自研图引擎

**不用 LangGraph、不用 pydantic-graph、不用 CrewAI。**

理由：
- 实际需要的能力很小（顺序节点 + 几个分支 + 一个回环 + 节点边界暂停 + 跨进程恢复）
- pydantic-graph 是"代码即图"，未来做拖拽编辑器反而碍事；自研一开始就是"图 = JSON 数据"，前端编辑后存 DB 即可
- 自研 ~400 LOC 核心 + ~150 LOC 持久化即可覆盖全部需求
- 数据结构 / 事件协议 / 节点状态机完全自控，跟项目其他模块（Chat 的 SSE、Notes 的 Blackboard）一脉相承
- 不绑第三方版本，不踩泛型/文档/生态等坑

### 2.4 图作为数据，而非代码

这是 day-1 必须做对的核心决策：

- 图存在 DB 里（`GraphTemplate.definition` JSONB）
- 引擎读这条数据来跑，不读硬编码常量
- 启动 run 时把模板**复制一份快照**到 `IngestionRun.graph_snapshot`
- run 永远用自己的副本，模板被改/删除不影响已跑的 run
- 类比：GitHub Actions 改 workflow 文件不影响已经在跑的 build

**好处**：未来加"前端拖拽编辑器"是纯增量（前端编辑→存模板→新 run 用新模板），无需改引擎、无需改 schema、无需迁移历史数据。

---

## 三、完全体能力清单 vs 首版交付

| 类别 | 完全体 | 首版交付 |
|---|---|---|
| **输入源** | DaisyWind 内部对话 | ✅ |
| | DeepSeek 分享链接 | ✅ |
| | 粘贴文本 | ✅ |
| | ChatGPT / Claude / Kimi 分享 | 📦 |
| **节点类型** | Source / Classifier / Outliner / HumanReview / Writer / Critic / Sink | ✅ |
| | Searcher（查 Notes / 联网） | 📦 |
| | Linker（关联已有 Note） | 📦 |
| | Tagger | 📦 |
| | AgentNode（内嵌 Orchestrator Agent） | 📦 |
| **编排能力** | 图驱动节点调度 | ✅ |
| | 回环（Critic → Writer，带迭代上限） | ✅ |
| | 节点边界暂停 / 跨进程恢复 | ✅ |
| | 大纲人确认（await_user） | ✅ |
| | 一段对话拆多篇 Note | 📦 |
| | 节点并行 fan-out | 📦 |
| **图模板** | 系统内置默认模板 | ✅ |
| | 用户创建/编辑/分享多模板 | 📦 |
| **前端** | Vue Flow 只读图 + 节点状态实时高亮 + await_user 交互 | ✅ |
| | 拖拽编辑 / 连线 / 节点参数表单 | 📦 |
| **可观察** | SSE 事件流 + 决策可视化 | ✅ |
| | Logfire trace | 📦 |
| **模型分级** | 每个节点独立 provider+model，前端可覆盖 | ✅ |

📦 = 架构已支持，首版不实例化（不写文件 / 写了不 register / 接口不暴露）。新增时纯增量。

---

## 四、核心架构

### 4.1 数据模型

```
GraphTemplate                       — 图模板（蓝图）
  - id, user_id (null = 系统内置)
  - name, description, version
  - definition: JSONB                — { nodes: [...], edges: [...], entry_node: ... }
  - is_system: bool
  - created_at, updated_at

IngestionRun                        — 一次 ingestion 任务
  - id, user_id
  - source_type, source_ref
  - template_id                      — 仅追踪来源，可空
  - graph_snapshot: JSONB            — 启动时复制模板进来，run 永远用自己的副本
  - status                           — pending|running|awaiting_user|succeeded|failed|cancelled
  - blackboard: JSONB                — 全部中间状态 + 节点状态 + 节点输出
  - created_at, updated_at, completed_at

IngestionEvent (append-only)        — 完整执行 trace，可重放
  - id, run_id, ts
  - actor                            — engine|<node_name>|user|system
  - kind                             — node_started|node_completed|node_failed|state_patched|edge_traversed|await_user|user_resume|run_completed|...
  - payload: JSONB
```

### 4.2 三个抽象基类（架构骨干，永不变）

```
SourceAdapter      .match(uri)                -> bool
                   .fetch(uri)                -> RawConversation

NodeType           .type_name / .display_name / .description
                   .params_schema             -> Pydantic model
                   .inputs / .outputs         -> 声明读/写 blackboard 哪些键
                   .run(ctx, params)          -> patch (dict)

GraphEngine        加载 graph_snapshot + blackboard
                   找 ready 节点 → 执行 → 写状态 → 解析出边 → 推进
```

**新增能力 = 新增子类 + register**，三个基类签名永不变。

### 4.3 图 Schema 数据结构

存于 `GraphTemplate.definition` 和 `IngestionRun.graph_snapshot`：

```json
{
  "entry_node": "source",
  "nodes": [
    {
      "id": "source",
      "type": "source",
      "params": { "source_type": "deepseek_share" },
      "position": { "x": 0, "y": 0 }
    },
    {
      "id": "classifier",
      "type": "classifier",
      "params": { "model": "deepseek-chat" },
      "position": { "x": 200, "y": 0 }
    },
    { "id": "writer", "type": "writer", "params": { "model": "deepseek-chat" }, "position": {...} },
    { "id": "critic", "type": "critic", "params": { "model": "deepseek-chat" }, "position": {...} },
    { "id": "sink", "type": "sink", "params": {}, "position": {...} }
  ],
  "edges": [
    { "id": "e1", "source": "source", "target": "classifier" },
    { "id": "e2", "source": "classifier", "target": "outliner" },
    { "id": "e3", "source": "outliner", "target": "human_review" },
    { "id": "e4", "source": "human_review", "target": "writer" },
    { "id": "e5", "source": "writer", "target": "critic" },
    { "id": "e6", "source": "critic", "target": "sink", "condition": "pass" },
    { "id": "e7", "source": "critic", "target": "writer", "condition": "fail", "back_edge": true, "max_iterations": 3 }
  ]
}
```

**字段说明：**
- `nodes[].type` 必须在节点类型注册表中存在
- `nodes[].params` 必须符合该 type 的 `params_schema`
- `nodes[].position` 用于前端布局（首版可由 dagre 自动布局生成，不强制存）
- `edges[].condition` 可选，运行时由源节点输出决定走哪条
- `edges[].back_edge` + `max_iterations` 标识回环边及上限

### 4.4 节点类型注册表 + 参数 Schema

每个 NodeType 注册时声明：

```python
class ClassifierNode(NodeType):
    type_name = "classifier"
    display_name = "意图分类"
    description = "判断对话价值 / 主题 / 是否值得归档"

    class Params(BaseModel):
        model: str = "deepseek-chat"
        provider: str = "deepseek"

    inputs = ["raw_conversation"]
    outputs = ["classification"]

    async def run(self, ctx, params): ...
```

通过 API 暴露：`GET /ingest/node-types` → 返回所有节点类型 + 它们的 params JSONSchema。
**首版前端不用此接口**，但接口必须存在（未来编辑器需要动态生成参数表单）。

### 4.5 图引擎执行循环

```
load run.graph_snapshot, run.blackboard

while True:
    ready_nodes = [n for n in nodes
                   if n.status == "pending"
                   and all(predecessor.status == "done" for predecessor in n.predecessors)]

    if not ready_nodes:
        if any(n.status == "running" or n.status == "awaiting") in current process: wait
        else: check terminal reached / mark run done
        break

    for node in ready_nodes:
        mark node "running" + emit node_started
        try:
            patch = await node_type.run(ctx, node.params)
            apply patch to blackboard
            mark node "done" + emit node_completed
            for edge in node.outgoing:
                if edge.condition not satisfied: skip
                if edge.back_edge and traversal_count[edge.id] >= edge.max_iterations: skip
                reset edge.target.status to "pending"
                increment traversal_count[edge.id] if back_edge
                emit edge_traversed
        except AwaitUserSignal:
            mark node "awaiting"
            run.status = awaiting_user
            emit await_user
            return  # exit worker, wait for resume
        except Exception as e:
            mark node "failed" + emit node_failed
            run.status = failed; return
```

**ARQ tick 进来 → 执行循环 → 节点边界遇到暂停就退出 → 下次 tick 接着跑。**

### 4.6 回环处理（带迭代上限的 back-edge）

- 边可声明 `back_edge: true` + `max_iterations: N`
- 引擎为每条 back-edge 维护计数器 `edge_traversal_count[edge_id]`，存于 blackboard
- 触发回环时 +1，超过上限则不再回退（自动接受当前结果或走另一分支）
- 防止 LLM 死循环重写

**首版默认配置**：`Critic → Writer` back-edge，`max_iterations: 3`。

### 4.7 节点 = PydanticAI Agent 包装

需要 LLM 的节点（Classifier / Outliner / Writer / Critic）内部是独立的 PydanticAI Agent：
- 自己的 system prompt
- 自己的 model（来自 `params.model`）
- 自带 retry / streaming
- 输出落到 blackboard 的对应键

**优势**：每个节点单测、独立换模型、Searcher / Linker 内部还可以再调 tool。

### 4.8 Blackboard

存于 `IngestionRun.blackboard` JSONB 字段：

```
{
  "raw_conversation": [...],
  "classification": {...},
  "outline": {...},
  "draft": "...",
  "critic_feedback": [...],
  "node_status": {
    "source": "done",
    "classifier": "done",
    "outliner": "done",
    "human_review": "awaiting",
    "writer": "pending",
    ...
  },
  "edge_traversal_count": { "e7": 1 },
  "decisions_log": [...]
}
```

Pydantic 模型用 `extra="allow"`，新字段不破坏老 run。
节点只输出 patch（dict），由 state 层合并。

### 4.9 人在回路（await_user）

```
节点 raise AwaitUserSignal(stage="outline_review", payload=outline)
  → 节点 status = awaiting
  → run.status = awaiting_user
  → emit await_user event
  → worker 退出
                                       ↓
前端 SSE 收到 await_user → 渲染对应 stage 的交互 UI
                                       ↓
用户提交 → POST /ingest/runs/{id}/resume → 写 user_resume event + 把用户输入写入 blackboard
                                       ↓
重新派发 ARQ task → 引擎重新进入循环 → 该节点 status 变 done，继续推进
```

**任何节点都能 await_user**，不只是 HumanReview。完全体里 Critic 不通过 / Linker 拿不准都可以触发。
首版仅 HumanReview 节点会 await。

### 4.10 SSE 事件协议

沿用 Chat 模块的设计哲学（`actor + kind + payload` 三件套）：

```
- run_started               { run_id, graph_snapshot }
- node_started              { node_id, node_type, params }
- node_streaming            { node_id, delta }              # Writer 流式
- node_completed            { node_id, output, duration, tokens }
- node_failed               { node_id, error }
- state_patched             { patch }
- edge_traversed            { edge_id, source, target, iteration? }
- await_user                { node_id, stage, payload }
- user_resume               { node_id, stage, input }
- critic_feedback           { score, issues }
- run_completed             { note_id }
- run_failed                { error }
```

前端据此驱动：
- Vue Flow 节点状态实时高亮
- 时间线 / trace 面板
- await_user 时弹出对应交互 UI

### 4.11 异步执行 — ARQ

**ARQ** = Async Redis Queue，原生 asyncio 后台任务队列，复用项目已有 Redis。

为什么必须 day-1 用：
- 一次 ingestion 可能跑 30s ~ 几分钟（多次 LLM 调用）
- HTTP 请求挂这么久不可接受
- 标准做法：HTTP 创建 run → 丢任务到队列 → worker 进程异步执行 → 前端 SSE 订阅进度
- 节点边界暂停天然契合"worker 退出 → 下次 tick 进来"的拉取式模型

---

## 五、前端 Vue Flow 集成

### 5.1 选型

**[Vue Flow](https://vueflow.dev)** —— React Flow 的 Vue 移植，业界标杆。

理由：
- 节点用 Vue 组件自定义，可融入 shadcn-vue 设计系统
- 自动布局插件（dagre）白送
- 状态实时刷新（节点 props 是 reactive，SSE 推 status 改变后自动重渲染）
- 拖拽编辑零成本升级（首版禁用，未来开关一开就有）
- MIT 许可，~80kb gzip
- 跟自研后端零耦合（后端给 `{nodes, edges}` 数据，前端纯渲染）

### 5.2 首版能力（只读模式）

- `nodes-draggable="false"` / `edges-updatable="false"` / `nodes-connectable="false"`
- 节点显示：图标 + 名称 + 状态徽章（pending / running / awaiting / done / failed）
- 节点点击 → 右侧抽屉显示该节点的 inputs / outputs / params（只读）
- 当前活动节点 pulse 动画
- await_user 节点高亮（边框闪烁）+ 显示 "等待你确认" 标识
- 自动横向布局（dagre LR direction）
- 缩放/平移可用

### 5.3 await_user 交互

await_user 节点高亮时，下方面板渲染对应 stage 的交互 UI：
- `outline_review` stage → 大纲编辑器（Markdown 或结构化表单）+ 确认 / 修改后确认 按钮
- 用户提交 → POST resume → run 继续 → 该节点变 done

### 5.4 完全体扩展（不在首版）

- 拖拽节点 / 连线 / 删除节点 / 创建模板
- 节点参数表单（基于后端 `node-types` API 返回的 JSONSchema 自动生成）
- 模板列表 / 选择不同模板启动 run
- 多模板分享 / 克隆

---

## 六、文件结构

```
backend/app/ingestion/
  models.py              GraphTemplate / IngestionRun / IngestionEvent
  schemas.py             Blackboard / RawConversation / events / graph schema
  state.py               Blackboard 读写 + patch 合并
  events.py              事件 emit + SSE 序列化（Logfire hook 留点）

  graph/
    schema.py            GraphSnapshot / NodeSpec / EdgeSpec 定义
    engine.py            执行循环 + 状态机 + 回环处理
    persistence.py       graph_snapshot + blackboard 读写
    validator.py         图合法性校验
    registry.py          节点类型注册表
    seed.py              系统内置默认模板的 seed 数据

  sources/
    base.py              SourceAdapter ABC + registry
    internal.py
    deepseek_share.py
    pasted.py
    # chatgpt.py / claude.py / kimi.py 后续添加

  nodes/
    base.py              NodeType ABC + Pydantic Agent 包装
    source.py
    classifier.py
    outliner.py
    human_review.py
    writer.py
    critic.py
    sink.py
    # searcher.py / linker.py / tagger.py / agent_node.py 后续添加

  runner.py              ARQ job entry
  api.py                 start / get / sse / resume / cancel
                         GET /templates / GET /node-types

frontend/src/
  views/notes/
    # ingestion 入口与列表挂在 Notes 模块内
  components/notes/ingestion/
    IngestEntry.vue          — 触发入口（粘 URL / 选会话 / 粘文本）
    IngestRunPanel.vue       — 运行面板容器
    GraphView.vue            — Vue Flow 渲染器
    nodes/
      SourceNode.vue
      ClassifierNode.vue
      ...                    — 各类型节点 Vue 组件
    NodeDetailDrawer.vue     — 节点详情抽屉
    AwaitUserPanel.vue       — await_user 时的交互 UI
    OutlineReview.vue        — 大纲确认表单
    EventTimeline.vue        — 事件流时间线
  stores/ingest.ts
  api/ingest.ts
```

---

## 七、模型配置策略

### 7.1 默认配置（首版）

**全部节点默认使用 `deepseek-chat`**，省事 + 成本低。

### 7.2 可配置性

- 每个节点的 `provider + model` 由 `node.params` 控制
- 启动 run 时可在前端覆盖默认 params（首版可通过启动接口透传，UI 后续做）
- 完全体可引入"模型分级 preset"（fast / balanced / premium），一键切换全部节点配置

---

## 八、输入源策略

### 8.1 DeepSeek 分享链接

通过 `httpx` 直接调用 DeepSeek 的非公开 API（已验证可行）：

```
GET https://chat.deepseek.com/api/v0/share/content?share_id={SHARE_ID}
```

返回完整结构化 JSON（`title` / `messages[]` / `fragments[]` / `inserted_at`），**无需 headless 浏览器、无需爬虫**。

合规说明：分享链接的诞生意味着内容已被用户主动 public，访问公开分享内容不构成侵权。

### 8.2 内部对话

直接读 DB（`Conversation` + `ChatMessage`），转换为统一的 `RawConversation` 格式。

### 8.3 粘贴文本

兜底方案，用户粘任意 Markdown / 纯文本，由 Classifier 判断是否可识别为对话结构。

### 8.4 后续扩展

每加一个平台 = 新增一个 `SourceAdapter` 子类 + registry 注册，不动核心。

---

## 九、前端入口决议

**ingestion 功能不在 Sidebar 加新模式，全部挂在 Notes 模块内。**

- 触发入口：Notes 模块内的"从对话生成"按钮（具体位置 toolbar / 列表上方 / 编辑页内待定）
- 运行状态追踪：进行中的 ingestion runs 列表也在 Notes 模块内展示
- 完成产物：自动落入 Notes 列表，与普通 Note 等同

---

## 十、已决议事项汇总

| # | 决议 | 时间 |
|---|------|------|
| 1 | 编排范式：Graph + Agent-in-Node 混合架构 | 2026-04-23 |
| 2 | 编排框架：自研图引擎，不用 LangGraph / pydantic-graph | 2026-04-23 |
| 3 | 图持久化：GraphTemplate 表 + IngestionRun.graph_snapshot 快照 | 2026-04-23 |
| 4 | Critic 回环：图层面 back-edge + 引擎限次（max_iterations: 3） | 2026-04-23 |
| 5 | 图 CRUD 写接口首版不暴露，未来直接新增 endpoint | 2026-04-23 |
| 6 | 前端图渲染：Vue Flow 只读模式，未来开拖拽编辑 | 2026-04-23 |
| 7 | Logfire 后期接入，不影响首版 | 2026-04-22 |
| 8 | 大纲阶段触发 await_user 人确认 | 2026-04-22 |
| 9 | 不做 MVP，架构 day-1 即完全体，首版只是少注册组件 | 2026-04-22 |
| 10 | 接受 DeepSeek 分享链接的"自分享自抓"灰区 | 2026-04-22 |
| 11 | 节点默认全部 deepseek-chat，前端可覆盖 | 2026-04-22 |
| 12 | 入口与运行追踪挂在 Notes 模块内 | 2026-04-22 |
| 13 | 异步执行用 ARQ，复用现有 Redis | 2026-04-22 |

---

## 十一、待定事项

- DB 表 `GraphTemplate` / `IngestionRun` / `IngestionEvent` 的 Tortoise model 与迁移落地方案确认
- ARQ 依赖引入与 worker 进程启动方式确认
- Notes 模块内 ingestion 入口的具体位置（toolbar / 列表上方 / 编辑页）
- 各节点的 system prompt 详细设计
- Vue Flow 节点组件视觉规范（融入 shadcn-vue 体系）
- 系统内置默认图模板的精确节点 / 边定义（含各节点初始 params）

---

## 十二、与 RAG（P2）的衔接

本模块产出的 Note 天然是高质量 RAG 语料：

- 已被 Critic 评审过质量
- 已被 Outliner 结构化（标题 / 章节）
- 已被 Tagger 打标签（完全体）
- 已被 Linker 关联到已有知识网络（完全体）

P2 启动时，RAG 索引器只需订阅"Note 写入"事件即可自动入库。
