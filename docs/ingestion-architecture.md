# Conversation Ingestion — 架构设计文档

> 把对话（DaisyWind 内部 / 外部分享链接 / 粘贴文本）通过多 Agent 编排整理成结构化 Note。
> 同时为后续 RAG 知识库提供高质量语料来源。
> 最后更新：2026-04-26

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

- 新增能力（新 Source / 新 Node 类型 / Logfire / 并行）= 纯增量
- 不动核心代码、不改 DB schema、不改事件协议
- 不存在"MVP 重写"，只有"功能逐步 enable"

### 1.4 明确不做的事（永久排除）

经过 2026-04-26 的设计 review，下列能力**明确不在本项目范围内**，不要再考虑：

- ❌ **前端拖拽式工作流编辑器**（Coze / Dify / n8n 风格）—— 暴露面广、被大厂垄断、个人项目收益低、简历价值低
- ❌ **用户级工作流编辑能力**（参数表单 / JSON 编辑器开放给终端用户）—— 个人验证平台无此需求
- ❌ **多模板用户分享 / 协作 / 权限**—— 单用户场景，过度设计

工作流定义改用 **Config-as-Code**（YAML 文件入 git）方式管理，详见 §4.10。

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
       前端 Timeline 视图：节点状态流式更新 + 节点输出可展开 +
       await_user 交互；不渲染图结构，不做编辑
```

**外层是图（Config-as-Code 定义），内层节点可以是 Agent（保留智能）。前端只观察、不编辑。**

### 2.2 范式选型对比

| 范式 | 适合度 | 备注 |
|---|---|---|
| Pure Agent Loop（LLM 主导） | ❌ | 可观测性差、不可干预 |
| Pure Pipeline | ❌ | 写死流程不灵活 |
| **Graph + Agent-in-Node** | ✅ | 业界共识方案 |
| Plan-and-Execute | ❌ | 计划本身就是任务的一部分 |
| Handoff / Routing | ❌ | 缺乏全局视野 |

### 2.3 框架选型：自研图引擎

**不用 LangGraph、不用 pydantic-graph、不用 CrewAI。**

理由：
- 实际需要的能力很小（顺序节点 + 几个分支 + 一个回环 + 节点边界暂停 + 跨进程恢复）
- 自研 ~400 LOC 核心 + ~150 LOC 持久化即可覆盖全部需求
- 数据结构 / 事件协议 / 节点状态机完全自控，跟项目其他模块（Chat 的 SSE）一脉相承
- 不绑第三方版本，不踩泛型/文档/生态等坑

### 2.4 图作为数据，而非代码

这是 day-1 必须做对的核心决策：

- 图存在 DB 里（`workflow_template.definition` JSONB）
- 引擎读这条数据来跑，不读硬编码常量
- 启动 run 时把模板**复制一份快照**到 `ingestion_run.graph_snapshot`
- run 永远用自己的副本，模板被改/删除不影响已跑的 run
- 类比：GitHub Actions 改 workflow 文件不影响已经在跑的 build

**好处**：未来若要改换 YAML schema、增加节点类型、调整 prompt——历史 run 永远用自己的快照不动，也能精确复现旧行为。

---

## 三、完全体能力清单 vs 首版交付

| 类别 | 完全体 | 首版 |
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
| **工作流定义** | Config-as-Code（YAML in git） | ✅ |
| | 启动时同步到 DB + 版本链管理 | ✅ |
| | 多套模板（多个 YAML 文件） | 📦 |
| | ~~用户拖拽编辑器~~ | ❌ 永久不做 |
| | ~~用户参数表单 / 草稿发布~~ | ❌ 永久不做 |
| **前端 UI** | Timeline 运行状态 + 节点输出可展开 + 流式更新 | ✅ |
| | await_user 交互面板 | ✅ |
| | 历史 run 列表 | ✅ |
| | ~~图结构可视化（Vue Flow / dagre）~~ | ❌ 永久不做 |
| **可观察** | SSE 事件流 + 节点级 token / 耗时 / 输出 | ✅ |
| | Logfire trace | 📦 |
| **模型分级** | 每个节点独立 provider+model（写在 YAML 里） | ✅ |

📦 = 架构已支持，首版不实例化（不写文件 / 写了不 register / 接口不暴露）。
❌ = 明确永久不做，不在产品范围内。

---

## 四、核心架构

### 4.1 数据模型（3 张表）

```
workflow_template                   — 工作流定义（来源：YAML 文件，启动时同步入库）
  - id (PK)
  - workflow_key                    — 业务标识，多版本共享同一 key
  - version                         — 单调递增整数
  - parent_version                  — 上一版本号（首版为 null）
  - definition: JSONB               — 启动时从 YAML 解析后写入
  - source_path                     — YAML 文件路径（追溯用）
  - is_system: bool                 — 系统内置（首版恒为 true）
  - created_at
  - UNIQUE(workflow_key, version)

ingestion_run                       — 一次执行的实例
  - id (PK), uuid (外部引用用)
  - user_id
  - source_type, source_ref         — 输入源类型 + 标识
  - template_id                     — 仅追踪来源，可空（指向 workflow_template）
  - graph_snapshot: JSONB           — 启动时复制 template.definition 进来
  - graph_schema_version: int       — graph_snapshot 的 schema 版本（11.3）
  - status                          — pending|running|awaiting_user|cancelling|cancelled|succeeded|failed
  - blackboard: JSONB               — 运行时状态 + 节点状态 + 节点输出
  - budget_tokens: int | null       — token 预算上限（11.5），null = 无限制
  - budget_cost_usd: decimal | null — 成本预算上限
  - awaiting_since: timestamp | null — 进入 awaiting_user 的时间（11.8）
  - locked_by: text | null          — worker 持锁标识（11.1）
  - locked_until: timestamp | null  — 锁过期时间
  - created_at, updated_at, completed_at

ingestion_event                     — append-only 执行 trace
  - id (PK)
  - run_id (FK → ingestion_run)
  - seq                             — per-run 单调递增（11.4 SSE 重放用）
  - ts
  - actor                           — engine|<node_id>|user|system
  - kind                            — node_started|node_completed|node_failed|state_patched|edge_traversed|await_user|user_resume|run_completed|...
  - payload: JSONB
  - UNIQUE(run_id, seq)
```

### 4.2 三个抽象基类（架构骨干，永不变）

```
SourceAdapter      .match(uri)                -> bool
                   .fetch(uri)                -> RawConversation

NodeType           .type_name / .display_name / .description
                   .params_schema             -> Pydantic model
                   .inputs / .outputs         -> 声明读/写 blackboard 哪些键
                   .idempotent: bool          -> 是否幂等（11.2）
                   .run(ctx, params)          -> patch (dict)

GraphEngine        加载 graph_snapshot + blackboard
                   找 ready 节点 → 执行 → 写状态 → 解析出边 → 推进
```

**新增能力 = 新增子类 + register**，三个基类签名永不变。

### 4.3 图 Schema 数据结构

存于 `workflow_template.definition` 和 `ingestion_run.graph_snapshot`：

```json
{
  "schema_version": 1,
  "entry_node": "source",
  "nodes": [
    {
      "id": "source",
      "type": "source",
      "params": { "source_type": "deepseek_share" }
    },
    {
      "id": "classifier",
      "type": "classifier",
      "params": { "model": "deepseek-chat", "system_prompt": "..." }
    },
    { "id": "writer", "type": "writer", "params": { "model": "deepseek-chat" } },
    { "id": "critic", "type": "critic", "params": { "model": "deepseek-chat" } },
    { "id": "sink", "type": "sink", "params": {} }
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
- `schema_version`：图 schema 版本号（11.3 兼容性管理）
- `nodes[].type` 必须在节点类型注册表中存在
- `nodes[].params` 必须符合该 type 的 `params_schema`
- `edges[].condition` 可选，运行时由源节点输出决定走哪条
- `edges[].back_edge` + `max_iterations` 标识回环边及上限
- 不再要求 `nodes[].position`（前端不渲染图结构）

### 4.4 节点类型注册表 + 参数 Schema

每个 NodeType 注册时声明：

```python
class ClassifierNode(NodeType):
    type_name = "classifier"
    display_name = "意图分类"
    description = "判断对话价值 / 主题 / 是否值得归档"
    idempotent = True

    class Params(BaseModel):
        model: str = "deepseek-chat"
        provider: str = "deepseek"
        system_prompt: str

    inputs = ["raw_conversation"]
    outputs = ["classification"]

    async def run(self, ctx, params): ...
```

通过 API 暴露：`GET /ingest/node-types` → 返回所有节点类型 + 它们的 params JSONSchema。
**首版前端不消费此接口**，但接口必须存在（用于运行时校验 YAML、未来扩展用）。

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
            run.awaiting_since = now()
            emit await_user
            return
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
- 自己的 system prompt（来自 YAML 的 `params.system_prompt`）
- 自己的 model（来自 `params.model`）
- 自带 retry / streaming
- 输出落到 blackboard 的对应键

**优势**：每个节点单测、独立换模型、Searcher / Linker 内部还可以再调 tool。

### 4.8 Blackboard

存于 `ingestion_run.blackboard` JSONB 字段：

```
{
  "raw_conversation": [...],
  "classification": {...},
  "outline": {...},
  "draft": "...",
  "critic_feedback": [...],
  "node_status": {
    "source": { "status": "done", "attempt": 1, "started_at": "..." },
    "classifier": { "status": "done", "attempt": 1, "started_at": "..." },
    ...
  },
  "edge_traversal_count": { "e7": 1 },
  "usage": { "tokens_total": 4823, "cost_total": 0.0032 },
  "decisions_log": [...]
}
```

Pydantic 模型用 `extra="allow"`，新字段不破坏老 run。
节点只输出 patch（dict），由 state 层合并。
`node_status[id]` 是对象（含 attempt、started_at），为 11.2 节点幂等留接口。

### 4.9 人在回路（await_user）

```
节点 raise AwaitUserSignal(stage="outline_review", payload=outline)
  → 节点 status = awaiting
  → run.status = awaiting_user
  → run.awaiting_since = now()
  → emit await_user event
  → worker 退出
                                       ↓
前端 SSE 收到 await_user → 在 timeline 中渲染对应 stage 的交互面板
                                       ↓
用户提交 → POST /ingest/runs/{id}/resume → 写 user_resume event + 把用户输入写入 blackboard
                                       ↓
重新派发 ARQ task → 引擎重新进入循环 → 该节点 status 变 done，继续推进
```

**任何节点都能 await_user**，不只是 HumanReview。完全体里 Critic 不通过 / Linker 拿不准都可以触发。
首版仅 HumanReview 节点会 await（大纲确认场景）。

### 4.10 Config-as-Code：工作流定义来自 YAML 文件

工作流定义不通过 UI 编辑，而是作为代码资产管理：

```
backend/app/ingestion/templates/
  default.yaml          ← 系统内置标准流程
  # long_form.yaml      ← 未来增加多模板就加文件
```

`default.yaml` 大致结构：

```yaml
key: default
version: 3
description: 标准对话整理流程
schema_version: 1
nodes:
  - id: source
    type: source
    params:
      source_type: deepseek_share
  - id: classifier
    type: classifier
    params:
      model: deepseek-chat
      provider: deepseek
      system_prompt: |
        你是一个对话价值判断专家...
  - id: writer
    type: writer
    params:
      model: deepseek-chat
      system_prompt: |
        你是一个笔记撰写专家...
  - id: critic
    type: critic
    params:
      model: deepseek-chat
      system_prompt: |
        你是一个笔记质量评审专家...
  # ... 其他节点
edges:
  - { from: source, to: classifier }
  - { from: classifier, to: outliner }
  - { from: outliner, to: human_review }
  - { from: human_review, to: writer }
  - { from: writer, to: critic }
  - { from: critic, to: sink, condition: pass }
  - { from: critic, to: writer, condition: fail, back_edge: true, max_iterations: 3 }
```

#### 同步机制

后端启动时（FastAPI lifespan）自动执行：

```
for yaml_file in scan(templates/*.yaml):
    spec = parse(yaml_file)
    validate_against_node_registry(spec)            # 节点 type / params 必须合法

    existing = SELECT FROM workflow_template
               WHERE workflow_key = spec.key AND version = spec.version
    if existing:
        if existing.definition != spec:             # 同 version 内容不同 → 报错
            raise ConflictError
        continue                                    # 已同步，跳过

    parent_version = SELECT MAX(version)
                     FROM workflow_template
                     WHERE workflow_key = spec.key
    INSERT workflow_template (
        workflow_key = spec.key,
        version = spec.version,
        parent_version = parent_version,
        definition = spec.to_graph_definition(),
        source_path = yaml_file,
        is_system = true,
    )
```

#### 改 prompt / 改流程的工作流

```
1. 编辑 templates/default.yaml
2. 把 yaml 顶部的 version: 3 改成 version: 4
3. git commit
4. 重启后端 → 自动 INSERT 新行
5. 之后启动的 run 用 v4
6. 老 run 的 graph_snapshot 是 v3 副本，永不受影响
```

#### 这套设计为什么是 production-grade

- **Airflow / GitHub Actions / dbt 都是这个模式**，业界成熟做法
- 配置入 git → 完整版本控制、code review、回滚能力
- 不依赖 UI 编辑器，**也比 UI 编辑器更可靠**（有 PR / diff / blame）
- 未来真要加用户级编辑，YAML 同步逻辑保留作为系统内置，用户编辑写入 DB 新行——并行不冲突

### 4.11 SSE 事件协议

沿用 Chat 模块的设计哲学（`actor + kind + payload` 三件套）：

```
- run_started               { run_id, graph_snapshot }
- node_started              { node_id, node_type, params }
- node_streaming            { node_id, delta }              # Writer 流式
- node_completed            { node_id, output, duration_ms, tokens }
- node_failed               { node_id, error }
- state_patched             { patch }
- edge_traversed            { edge_id, source, target, iteration? }
- await_user                { node_id, stage, payload }
- user_resume               { node_id, stage, input }
- run_completed             { note_id }
- run_failed                { error, reason? }
- run_cancelled             { reason? }
```

每个事件携带递增的 `seq`（写入 `ingestion_event.seq`），前端可断点重连：
`GET /ingest/runs/{id}/events?since={seq}`。

### 4.12 异步执行 — ARQ

**ARQ** = Async Redis Queue，原生 asyncio 后台任务队列，复用项目已有 Redis。

为什么必须 day-1 用：
- 一次 ingestion 可能跑 30s ~ 几分钟（多次 LLM 调用）
- HTTP 请求挂这么久不可接受
- 标准做法：HTTP 创建 run → 丢任务到队列 → worker 进程异步执行 → 前端 SSE 订阅进度
- 节点边界暂停天然契合"worker 退出 → 下次 tick 进来"的拉取式模型

---

## 五、前端：Timeline 观察界面

### 5.1 设计原则

**前端不渲染图结构，不允许编辑，只观察。**

理由：
- 工作流定义来自 YAML（开发者通过 git 改），无需 UI 编辑能力
- 首版图固定（默认模板），用户已知流程是什么，无需可视化结构
- 砍掉 Vue Flow / dagre / SVG 渲染，前端工程量降为原方案的 1/4

### 5.2 Timeline 视图（运行状态）

```
┌──── Run #abc123 · 标准对话整理 v3 ────┐
│ 来源：DeepSeek 分享链接 ...            │
│ 状态：⏳ 运行中 (3/7)                  │
│ ─────────────────────────────────────  │
│ ● Source        ✓ 0.2s                 │
│   └ 拉取 12 条消息                     │
│                                         │
│ ● Classifier    ✓ 1.4s    [展开输出]   │
│   └ 类型：技术深度对话                  │
│      价值评分：8.5                      │
│      tokens: 1.2k / $0.0008             │
│                                         │
│ ● Outliner      ✓ 3.1s    [展开输出]   │
│                                         │
│ ◐ Writer        ⏳ 流式生成中...       │
│   └ "## 引言\n这次对话围绕..."         │
│                                         │
│ ○ Critic        待执行                  │
│ ○ Sink          待执行                  │
│ ─────────────────────────────────────  │
│ 总计：tokens 4.8k · 耗时 12s · $0.003  │
│ [取消运行]                              │
└─────────────────────────────────────────┘
```

实现：纯 shadcn-vue 组件 —— `Card` + `Collapsible` + `Badge` + 一个垂直分隔线，**不引入 Vue Flow / dagre / SVG**。

### 5.3 节点状态视觉规范

| 状态 | 图标 | 颜色 | 行为 |
|---|---|---|---|
| pending | ○ | 灰 | — |
| running | ◐ | 蓝（脉动动画） | 显示流式 delta |
| awaiting | ⏸ | 橙（呼吸光晕） | 高亮 + 渲染交互面板 |
| done | ● | 绿 | 输出可展开（折叠默认） |
| failed | ✕ | 红 | 展开默认显示 error |
| skipped | ⊘ | 灰 | 极淡 |

### 5.4 await_user 交互

await_user 节点高亮时，timeline 中该节点位置展开为交互面板：
- `outline_review` stage → 大纲编辑器（Markdown 或结构化表单）+ 「确认」/「修改后确认」按钮
- 用户提交 → POST resume → run 继续 → 该节点变 done

### 5.5 历史 run 列表

Notes 模块内单开一个"整理记录"页：
- 列出当前用户的所有 ingestion_run
- 显示 status / 来源 / 创建时间 / 产出 Note 链接
- 点击进入 timeline 详情页（即 §5.2）
- 进行中的 run 顶部置顶

### 5.6 触发入口

参见 §9 —— 入口在 Notes 模块内。

---

## 六、文件结构

```
backend/app/ingestion/
  models.py              workflow_template / ingestion_run / ingestion_event
  schemas.py             Blackboard / RawConversation / events / graph schema
  state.py               Blackboard 读写 + patch 合并
  events.py              事件 emit + SSE 序列化（含 seq 维护，Logfire hook 留点）
  lock.py                Redis Run 级互斥锁封装（11.1）
  authz.py               get_owned_run_or_404 dependency（11.6）

  templates/             ★ Config-as-Code 入口
    default.yaml         系统内置标准流程
    # 后续多模板增加 yaml 文件

  graph/
    schema.py            GraphSnapshot / NodeSpec / EdgeSpec 定义
    engine.py            执行循环 + 状态机 + 回环处理
    persistence.py       graph_snapshot + blackboard 读写
    validator.py         图合法性校验 + YAML schema 校验
    registry.py          节点类型注册表
    sync.py              ★ YAML → DB 启动时同步逻辑
    migrators/           ★ schema_version 迁移占位（11.3）
      __init__.py

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

  runner.py              ARQ job entry（含锁获取 / cancel 检查）
  api.py                 start / get / sse / resume / cancel
                         GET /node-types
  cron.py                定期清理 awaiting_since 过期 run（11.8，首版可不上线）

frontend/src/
  views/notes/
    # ingestion 入口与列表挂在 Notes 模块内
  components/notes/ingestion/
    IngestEntry.vue          — 触发入口（粘 URL / 选会话 / 粘文本）
    RunListPanel.vue         — 历史 run 列表
    RunTimeline.vue          — Timeline 主视图
    NodeStep.vue             — Timeline 中单个节点的卡片（含状态、输出、流式）
    AwaitUserPanel.vue       — await_user 时的交互 UI
    OutlineReview.vue        — 大纲确认表单
  stores/ingest.ts
  api/ingest.ts
```

**已删除（曾设计但确认不做的）**：
- ~~components/notes/ingestion/GraphView.vue~~（Vue Flow 图视图）
- ~~components/notes/ingestion/nodes/*Node.vue~~（节点 Vue Flow 自定义组件）
- ~~components/notes/ingestion/NodeDetailDrawer.vue~~（节点参数编辑抽屉）
- ~~workflow editor / draft / publish 相关一切~~

---

## 七、模型配置策略

### 7.1 默认配置（首版）

**全部节点默认使用 `deepseek-chat`**，省事 + 成本低。

### 7.2 可配置性

- 每个节点的 `provider + model + system_prompt` 由 YAML 中 `params` 控制
- 改模型 / prompt = 改 YAML + version 自增 + 重启后端
- 不暴露给终端用户配置（开发者通过 git 管理）

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
- 运行状态追踪：进行中的 ingestion run 列表也在 Notes 模块内展示
- 完成产物：自动落入 Notes 列表，与普通 Note 等同

---

## 十、已决议事项汇总

| # | 决议 | 时间 |
|---|------|------|
| 1 | 编排范式：Graph + Agent-in-Node 混合架构 | 2026-04-23 |
| 2 | 编排框架：自研图引擎，不用 LangGraph / pydantic-graph | 2026-04-23 |
| 3 | 图持久化：workflow_template 表 + ingestion_run.graph_snapshot 快照 | 2026-04-23 |
| 4 | Critic 回环：图层面 back-edge + 引擎限次（max_iterations: 3） | 2026-04-23 |
| 5 | 不做用户级图编辑 / 拖拽 / 草稿 / 发布机制 | 2026-04-26 |
| 6 | 工作流定义采用 Config-as-Code（YAML 文件入 git） | 2026-04-26 |
| 7 | 启动时同步 YAML → workflow_template，新 version 自动 INSERT | 2026-04-26 |
| 8 | 前端不渲染图结构，改用 Timeline + Card 列表观察 | 2026-04-26 |
| 9 | 不引入 Vue Flow / dagre / SVG 图渲染相关依赖 | 2026-04-26 |
| 10 | Logfire 后期接入，不影响首版 | 2026-04-22 |
| 11 | 大纲阶段触发 await_user 人确认 | 2026-04-22 |
| 12 | 不做 MVP，架构 day-1 即完全体，首版只是少注册组件 | 2026-04-22 |
| 13 | 接受 DeepSeek 分享链接的"自分享自抓"灰区 | 2026-04-22 |
| 14 | 节点默认全部 deepseek-chat，YAML 内可覆盖 | 2026-04-22 |
| 15 | 入口与运行追踪挂在 Notes 模块内 | 2026-04-22 |
| 16 | 异步执行用 ARQ，复用现有 Redis | 2026-04-22 |

---

## 十一、生产级扩展性决议

> 原则：day-1 不全实现，但每项都留好"未来纯增量启用"的钩子。钩子代价 ≤ 10 行代码或 1 个字段，事后改要迁移历史 run 的项必须 day-1 落地。

### 11.1 Run 级互斥锁

- **决议**：Redis `SET key NX EX` 原语，`key = ingest:lock:run:{run_id}`，TTL = 节点最大执行时长 × 2（首版 600s）
- **Day-1 留口子**：ARQ job entry 进来先 `acquire_lock`，拿不到直接 return（不重试）；释放在 `finally`
- **未来 enable**：完全体不用改，只调 TTL；如换 Postgres advisory lock 也只动 `runner.py` 一处

### 11.2 节点幂等 / attempt 计数

- **决议**：`blackboard.node_status` 从字符串改为对象 `{ "status": "running", "attempt": 1, "started_at": ... }`；节点 run 前先 `attempt += 1`，记 `started_at`
- **Day-1 留口子**：NodeType 增加类属性 `idempotent: bool = False`，首版纯 LLM 节点标 `True`，副作用节点（Sink 写 DB）标 `False`；schema 字段先存好
- **未来 enable**：引擎按 attempt + idempotent 自动 retry

### 11.3 graph_snapshot schema_version

- **决议**：`graph_snapshot` 顶层加 `"schema_version": 1`；引擎启动时 `if schema_version not in ENGINE_SUPPORTED: raise`
- **Day-1 留口子**：定义 `ENGINE_SUPPORTED = {1}`（set，未来可同时支持多版本）；`graph/migrators/` 目录建好放空 `__init__.py`，证明迁移路径存在
- **未来 enable**：v2 上线时引擎读老 run 自动调 migrator → 升级到内存 v2 结构 → 不写回 DB（保留原始快照不可变）

### 11.4 SSE 事件 seq + 断点重放

- **决议**：`ingestion_event` 表加单调递增 `seq` 字段（per run，`MAX(seq)+1`）；SSE endpoint 支持 `?since={seq}` query
- **Day-1 必须做**：`seq` 字段建表时就加（事后回填很痛苦）
- **未来 enable**：前端 EventSource 断线重连时带 `since=lastSeq`，后端 `WHERE seq > since ORDER BY seq` 重放

### 11.5 Run 级 budget cap

- **决议**：`ingestion_run` 加 `budget_tokens: int | null` 和 `budget_cost_usd: decimal | null` 字段；blackboard 累加 `usage.tokens_total` / `usage.cost_total`；每个节点完成后引擎检查超限 → 标 `failed(reason=budget_exceeded)`
- **Day-1 留口子**：字段建好；首版默认 `null` = 无限制；累加逻辑写好（SSE 里已有 tokens）
- **未来 enable**：启动 run 时传 budget；超限 UI 渲染明确原因

### 11.6 Resume / Cancel authz

- **决议**：所有 `/ingest/runs/{id}/*` 接口在 dependency 层统一校验 `run.user_id == current_user.id`，404（不是 403）防止存在性泄漏
- **Day-1 必须做**：安全底线。封装成 `get_owned_run_or_404` dependency，所有 endpoint 强制使用
- **未来 enable**：加共享/协作时放开（加 `RunCollaborator` 表，dependency 内 `OR` 一下）

### 11.7 取消语义

- **决议**：分两层
  - **节点边界取消**（默认）：用户点取消 → `run.status = cancelling`；当前节点跑完后引擎检查到 cancelling → 标 cancelled，不再调度
  - **节点内取消**（完全体）：节点 run 接收 `ctx.cancel_token`（asyncio.Event），LLM 调用配合 token 立即中断
- **Day-1 留口子**：`NodeContext` 类签名里就带 `cancel_token` 字段（首版节点不消费它）；run.status 加 `cancelling` 中间态
- **未来 enable**：节点内部按需消费 token，无需改引擎

### 11.8 Awaiting_user TTL / 僵尸清理

- **决议**：`ingestion_run` 加 `awaiting_since: datetime | null`；进入 awaiting_user 时 set，resume 时 clear；ARQ cron 每小时扫 `awaiting_since < now - 7d` 的 run → 标 `cancelled(reason=user_timeout)`
- **Day-1 必须做**：字段建好（事后加要迁移）
- **未来 enable**：注册 ARQ cron job；可加用户提醒（如果有邮件系统）

### 11.9 Day-1 落地汇总

| 类别 | day-1 必须做 | 仅留字段/钩子 |
|---|---|---|
| DB schema | 11.4 seq, 11.5 budget 字段, 11.8 awaiting_since | 11.2 node_status 改对象结构 |
| 引擎核心 | 11.1 锁, 11.3 schema_version 校验, 11.6 authz dep, 11.7 cancelling 状态 | 11.2 attempt 累加, 11.5 budget 累加 |
| 协议 | — | 11.4 SSE since 参数（前端不消费） |
| 文件占位 | — | 11.3 migrators 目录 |

**day-1 实写代码量预估**：Redis 锁封装（~30 行）+ authz dependency（~10 行）+ 3 个 DB 字段 + `schema_version` 常量校验。其余均为字段预留 + 文档决议。

---

## 十二、待定事项

- DB 表 `workflow_template` / `ingestion_run` / `ingestion_event` 的 Tortoise model 完整字段清单（含索引、约束）
- ARQ 依赖引入与 worker 进程启动方式确认
- Notes 模块内 ingestion 入口的具体位置（toolbar / 列表上方 / 编辑页）
- 各节点 system prompt 详细设计（写在 `templates/default.yaml` 内）
- Timeline UI 视觉规范细节（节点状态过渡动画、流式 delta 渲染时机）
- 系统内置默认 YAML 模板的精确节点 / 边定义（含各节点初始 params）
- ARQ cron 启动方式（11.8 僵尸清理）

---

## 十三、与 RAG（P2）的衔接

本模块产出的 Note 天然是高质量 RAG 语料：

- 已被 Critic 评审过质量
- 已被 Outliner 结构化（标题 / 章节）
- 已被 Tagger 打标签（完全体）
- 已被 Linker 关联到已有知识网络（完全体）

P2 启动时，RAG 索引器只需订阅"Note 写入"事件即可自动入库。
