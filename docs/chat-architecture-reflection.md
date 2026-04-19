# Chat 架构反思记录

> 日期：2026-04-19
> 背景：Chat P1 完成后，对 `backend/app/api/v1/chat/stream.py` 和 `frontend/src/stores/chat.ts` 中的代码重复感产生架构疑问，经过一轮深度讨论后沉淀此文。
> 用途：下次重构前对齐思路；后续 P2/P3 新加 block 类型时作为判断依据。

---

## 1. 起点：那个"怪怪的"感觉

P1 完成后，观察到两处代码有"说不出的怪":

- `stream.py` 的 `stream_generator` 函数接近 200 行，做了 4 件事（事件翻译 / SSE 产出 / in-memory 聚合 / 持久化），内部维护三张索引表 + 一个 buffer。
- `chat.ts` 的 `sendMessage`（流式构造）和 `loadConversation`（DB 回放构造）是两条平行路径，产出同一种 `RenderBlock`。

问题："是我见识少，还是架构确实不优雅？"

---

## 2. 诊断：三个参照系的冲突

所有"怪味"的根源不是代码写得烂，而是**同时在对齐三个参照系**，扭曲发生在它们的接缝处：

| 参照系 | 给的约束 | 给的好处 |
|---|---|---|
| **PydanticAI** | 跨轮 `part.index` 重置 / server-side tool 执行 / 自动 loop | Agent 框架省手写循环 |
| **Anthropic 协议** | 事件种类固定 / block 是一等公民 / tool 客户端执行 | 设计哲学干净、可读 |
| **自己的 UI 需求** | `display_name` / `input_preview` / `collapsed` / 3D spinner 位置 | 用户体验 |

两两冲突点：

- **PydanticAI ↔ Anthropic**：server-side tool 结果在 Anthropic 协议里没位置
- **Anthropic ↔ UI**：纯净 wire protocol 不带 UI metadata
- **PydanticAI ↔ UI**：PydanticAI 只管 LLM，不管前端

**这不是能力问题，是任何人做这种系统都会遇到的张力。**

---

## 3. 四个决策（已定稿）

### 决策 1：协议哲学 — UI protocol（服务于当前 Vue 前端）

选项：wire protocol（纯数据）vs UI protocol（带 UI metadata）

**选定：UI protocol，服务对象明确为"当前的 Vue 前端"**。

理由：
- 项目是"学习 + 处子作 + 自用"定位，单前端且以后不换。
- UI 友好的字段（`tool_display_name` / `input_preview` / `result_summary` / `status`）直接放协议里，前端零负担。
- 日后如有全新思路会另起新项目换技术栈，不为"多前端复用"预留成本。

**但仍要守住一条边界**：

| 字段类型 | 举例 | 是否进协议 |
|---|---|---|
| 信息（人类可读的业务数据） | `tool_display_name`, `input_preview`, `result_summary`, `result_data`, `status` | 进 |
| 呈现（组件级 UI state） | `collapsed`, `isLastBlock`, `shouldBlink` | 不进，前端自己维护 |

即使选 UI protocol，后端也不代管 Vue 组件的局部状态。

### 决策 2：Block 作为主轴，tool_result 做成 block type

选项：`tool_result` 作为专属事件 vs 作为 `content_block` 的一个 `type`

**选定：block 作为主轴，`tool_result` 是一个 block type，不是独立事件**。

未来协议形态（目标）：

```
message_start
content_block_start    (type: "text" | "tool_use" | "tool_result" | "thinking" | "citation" | ...)
content_block_delta    (type: "text_delta" | "input_json_delta" | ...)
content_block_stop
...
message_delta          (usage, stop_reason)
message_stop
error
```

**协议事件种类固定（7 种左右），block 种类通过 `content_block.type` 判别。加新 block 类型协议本身零改动。**

与 Anthropic 原始协议的差别：多了 `type: "tool_result"` 这一种 block。这是**诚实的扩展**，不是偏离——因为 server-side tool execution 是 Anthropic 协议覆盖不到的业务场景。

### 决策 3：引入 BlockHandler 抽象（等真实需求驱动再做）

选项：保持 switch(event) vs 抽 handler 类

**选定：要抽，但不现在抽。等 P2 加第一个新 block 类型时顺手抽。**

目标形态：

```
每种 block 一个 handler，职责：
  - accumulator: 怎么累积 delta（流式用）
  - from_final: 怎么从 DB 的 ContentBlock 一次性构造终态（回放用）
  - serializer: 怎么落库
```

好处：
- 加新 block = 写一个新 handler 类，不动已有代码（开闭原则）
- 同一个 handler 被流式和回放复用 → 天然解决 `chat.ts` 两条路径重复的问题
- 每种 block 的生命周期逻辑聚在一个文件里，不再散在 switch 各 case

原则：**Rule of Three 触发后再抽**。现在只有 `text` / `tool_use` 两种，样本不足，硬抽容易抽错。P2 加 `citation` 时是黄金时机。

### 决策 4：继续用 PydanticAI（关在薄适配层里）

选项：继续 PydanticAI vs 自写 agent loop

**选定：继续 PydanticAI。但把它的 event 抽象关在薄适配层里，不让它漏到 handler 和协议层。**

理由：
- 当前规模（1-2 Agent + 标准 tool use），框架 vs 手写差距很小。
- 自写 loop 的核心就是 30 行 while 循环，不神秘，随时可拆。
- 当真碰到非标准控制流（orchestrator / human approval / 动态上下文注入）时，那时拆才有真实驱动，拆得不冤枉。

**分类认知**（避免下次混淆）：

- **框架管 loop**：PydanticAI / LangChain / LangGraph / DeepAgents / OpenAI Agents SDK / Spring AI / Claude Agent SDK
- **自己管 loop**：原始 `anthropic` / `openai` / `google-genai` SDK（Cursor / Claude Code / Cline 用的是这类）

两类不是竞争关系，是不同层级。你现在在第一类，没问题。

---

## 4. 未来 block 类型预测（用于压力测试协议设计）

一年内预计会出现的 block 类型：

| Block | 触发时机 | 复杂度 |
|---|---|---|
| `thinking` | 接入 DeepSeek-R1 / Claude extended thinking / Gemini thinking | 低（类似 text，UI 折叠变灰） |
| `image` | P2 多模态消息 | 中（input/output 两种方向） |
| `citation` / `rag_source` | P2 RAG 上线 | 中（要有"点击跳转原笔记"交互） |
| `code_execution` | Phase 3 代码沙箱 | 高（流式 stdout/stderr + 退出码） |
| `artifact` | 仿 Claude artifact | 高（影响整体布局） |
| `handoff` / `subagent_call` | Orchestrator 模式 | 高（嵌套结构） |
| `error`（block 级） | tool 失败但 agent 继续 | 低 |
| `form` / `approval` | human-in-the-loop | 中（交互式） |

**判据**：任何新 block 类型接入时，如果必须新开专属事件、或必须改协议事件种类，说明当前协议不对，要回头改。**好的协议应该让新 block 只多一个 type 值，其他不动。**

---

## 5. 关键 mental model

### 5.1 三种数据形状是必要的，形状之间的映射才是可以收敛的

| 形状 | 职责 | 独有字段 |
|---|---|---|
| DB 格式 (`ContentBlock`) | 持久化 + 查询 | 稳定字段，无临时态 |
| 前端渲染态 (`RenderBlock`) | UI 状态机 | `status`, `collapsed`, `partialInputJson`, `inputPreview` |
| 后端累积 dict | 流式过程暂存 | 未解析的 delta 中间态 |

三种形状合并 = 反模式。真正要收敛的是**三种形状之间的映射函数**，现在这些映射散在多处手写，抽出来集中维护即可。

### 5.2 DB 回放 = 流式的"快进"

```
流式:     SSE events ─→ Accumulator ─→ RenderBlock
回放:     DB blocks  ─→ Accumulator ─→ RenderBlock
                         ↑ 同一个
```

回放不经过 delta 拼接，但"最终形态 → RenderBlock"的规则必须和流式结束后的规则一致。现在两边各写一份是真重复。

### 5.3 协议的两层 event 要分清

```
PydanticAI events   (框架给的)       ─┐
                                       ├─→ 在 stream.py 做翻译
你的 SSE events     (你发给前端的)    ─┘
```

前者无法控制（`part.index` 跨轮重置就是它的抽象漏出来），后者**完全由你设计**。别把两者搅在一起讨论。

### 5.4 dispatch 主轴换位

以前：`switch(event)`，每种 block 要在多个 case 里加 `if type === 'xxx'`。
以后：`handlers[blockType].apply(event, ...)`，每种 block 一个 handler。

**event 还在、SSE 还在、PydanticAI 也还在**，只是"dispatch 的第一个问题"从"这是什么事件"变成了"这影响哪种 block"。

### 5.5 "Client" 在 Anthropic 语境下不是浏览器

Anthropic 说 "tool execution on the client" 指的是**调用 Anthropic API 的那段代码**——在我的架构里就是 FastAPI 后端。**工具永远在 Python 后端跑**，这个跟 Anthropic 风格不冲突。改成 Anthropic 风格 ≠ 把工具搬去前端。

---

## 6. 行动计划

分阶段，按**风险/收益**排序：

### 阶段 A：想清楚（纯脑力，零风险）✅ 本次讨论已完成

- [x] 决定协议哲学（UI protocol, 服务当前 Vue 前端）
- [x] 决定 tool_result 作为 block type
- [x] 预测未来 block 类型
- [x] 决定 loop 编排者（保留 PydanticAI）

### 阶段 B：字段命名对齐（低风险，高心理收益）✅ 已完成

- [x] 统一 `id` vs `toolCallId`、`name` vs `toolName` 等命名，前后端选一套风格贯彻到底（统一去掉了 `tool_` 前缀）。
- [x] 确认字段分类表（哪些进协议、哪些留前端），清理 `collapsed` 等"呈现字段"是否被错误地放进了协议。

### 阶段 C：抽出 `ContentBlock → RenderBlock` 映射层（中风险，独立收益）

- [ ] 把 `chat.ts` 里 `loadConversation` 的 DB block 转 RenderBlock 逻辑抽成纯函数
- [ ] 让 `sendMessage` 里流式收尾的逻辑尽可能复用同一套映射
- [ ] 这一步**不涉及**协议改动和 handler 抽象，纯消除重复

### 阶段 D：引入 BlockHandler 抽象（等 P2 加 citation 时做）

- [ ] 基于阶段 A 的协议决定，设计 handler 接口
- [ ] 先抽 `text` + `tool_use`（保持行为等价）
- [ ] 加第 3 种（`citation` 或 `thinking`）验证抽象是否对
- [ ] **不要提前做**，Rule of Three 没触发之前硬抽必错

### 阶段 E：tool metadata 同源化（顺手做）✅ 已完成

- [x] 把 `TOOL_DISPLAY_NAMES` 从 `stream.py` 移走
- [x] **决策变更**：彻底放弃 `display_name` 概念，前端直接显示原生的 `block.name`。前后端协议极度精简。

### 阶段 F：协议升级为 "block 主轴"（最晚，改动最大）

- [ ] `tool_use_start/delta/stop/result` 这组专属事件并入通用 `content_block_*`
- [ ] `tool_result` 成为一个 `content_block.type`
- [ ] 前后端同步升级，需要 P2 前做好还是 P2 中做要看 `citation` block 首次接入的时机

---

## 7. 元原则

这次反思沉淀下来的三条原则，下次写新代码时守住：

1. **思考走在前面，抽象跟在需求后面**。抽象不是重构出来的，是想清楚出来的；但也不能空想抽象，要等真实的第 3 个实例出现再动手。
2. **信息进协议，呈现留前端**。每加一个字段都问一遍："这是任何前端都需要的业务信息，还是某个组件的局部状态？"
3. **参照系想清楚再开始模仿**。学 Anthropic、学 Vercel、学 Cursor 都可以，但不要同时学三个——它们的设计哲学不兼容，混血一定露馅。

---

## 8. 决议卡片（给未来的自己）

遇到新需求时快速查询的单行清单：

- 加一种新 block 类型？→ 新增一个 `content_block.type` 值 + 写一个 BlockHandler 类（阶段 D 之后）
- 加一个 tool？→ tool 模块自带 metadata，注册表自动暴露（阶段 E 之后）
- 前端要新的 UI 状态（比如"hover 高亮"）？→ 前端组件内维护，不要发 SSE 事件
- 要支持新 LLM provider？→ 扩 `providers.py` 工厂，不动协议
- 要做 orchestrator / 多 Agent？→ 届时可能要拆 PydanticAI，评估决策 4 是否还成立
- 要做移动端？→ 按当前 UI protocol 的边界走（"信息进 / 呈现不进"），协议应当够用；如果不够用，说明之前的边界划错了

---

## 9. 参考文件

- `backend/app/api/v1/chat/stream.py` — 当前 SSE 事件生成与 PydanticAI 适配
- `frontend/src/stores/chat.ts` — 当前流式消费 + DB 回放
- `frontend/src/components/chat/ToolUseBlock.vue` — 当前 tool_use 渲染
- `backend/app/schemas/chat_schema.py` — 当前 block Pydantic schema
- `backend/app/tools/` — tool 定义目录（未来 metadata 同源化的落脚点）
- `docs/streaming-render.md` — 当前 SSE 协议文档
- `docs/chat-architecture.md` — Chat 模块原始架构设计
