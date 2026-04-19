# Phase B Execution Brief — Naming Alignment

> 这份文档是一个**执行 brief**，给另一个 agent 看。目标 agent 不需要知道更大的架构讨论，只需要精确按照本文档执行即可。
> 背景 context 见 `docs/chat-architecture-reflection.md`（非必读，只在遇到边界模糊时参考）。

---

## 1. 目标

消除 Chat 模块 SSE 协议和前端渲染态中不必要的 `tool_` 前缀字段，统一为 Anthropic / OpenAI 风格的命名（`id` / `name` / `display_name` / `input_preview`）。

**只做命名对齐。不抽象、不重构逻辑、不移动代码、不动 DB schema。**

---

## 2. 基本规则（必读）

### 2.1 命名哲学

- **后端统一 snake_case**（Python 惯例）
- **前端 TypeScript 的 SSE payload 接口**字段名**必须与后端 SSE 实际发送的 key 完全一致**（snake_case），因为是 wire format
- **前端内部类型（RenderBlock 等）用 camelCase**（TS 惯例）
- **块内核心字段对齐 Anthropic 语义**：tool_use block 的 `id` / `name` / `input` / `status` / `output`（不加 `tool_` 前缀）

### 2.2 什么该改 vs 什么不该改

**该改**：SSE 事件 payload 的字段名、前端 RenderBlock 的 `toolCallId` / `toolName` / `toolDisplayName`、前端 SSE Payload 接口的字段名。

**不该改**：
- `backend/app/schemas/chat_schema.py` 里的 `ToolUseBlock` pydantic 模型（DB 格式，已经是 Anthropic 命名）
- `backend/app/services/chat_service.py` 里的 `tool_call_id=...` / `tool_name=...`（这是 **PydanticAI 的 ToolCallPart / ToolReturnPart 构造器参数**，是框架 API 不是我们的字段）
- DB 里的历史数据（不需要迁移，因为 DB 格式就是 Anthropic 格式，从未用 `tool_` 前缀）
- `inputPreview` / `partialInputJson` / `resultSummary` / `resultData` 这些**本来就没有 `tool_` 前缀**的字段（只改有前缀的）

### 2.3 用户偏好（来自 `CLAUDE.md`）

- 中文交流
- 改代码前先描述要做什么，等用户确认再动手
- 不做未要求的额外改动
- 图标库固定 `@phosphor-icons/vue`
- 不创建新文档文件（本次不需要创建）

---

## 3. 精确改动清单

### 3.1 后端 `backend/app/api/v1/chat/stream.py`

SSE 事件的 payload key 改名：

**`tool_use_start` 事件（第 123-129 行左右）**
```
tool_call_id       → id
tool_name          → name
tool_display_name  → display_name
tool_input_preview → input_preview
```

**`tool_use_delta` 事件（第 141-146 行左右）**
```
tool_call_id → id
```
（`type` / `partial_json` / `index` 不变）

**`tool_use_stop` 事件（第 164-167 行左右）**
```
tool_call_id → id
```

**`tool_result` 事件（第 187-194 行左右）**
```
tool_call_id → id
tool_name    → name
```
（`result_summary` / `result_data` / `status` / `index` 不变）

**注意**：
- `stream.py` 里 `TOOL_DISPLAY_NAMES` 字典本身不动（这是 Phase E 的事）。
- 内部 in-memory `blocks` list 里 dict 的 key 已经是 Anthropic 命名（`id` / `name` / `input` / `status` / `output`），不要动。
- 局部变量名（如 `tool_call_id = event.part.tool_call_id`、`tool_name = event.part.tool_name`）**保留不改**——它们读的是 PydanticAI 的属性，是框架的命名。

---

### 3.2 前端类型定义 `frontend/src/types/chat.ts`

**SSE Payload 接口（第 60-88 行的 P1 Tool 事件 Payload 区块）**

```ts
// 改前
export interface ToolUseStartPayload {
  index: number
  tool_call_id: string
  tool_name: string
  tool_display_name: string
  tool_input_preview: string
}

// 改后
export interface ToolUseStartPayload {
  index: number
  id: string
  name: string
  display_name: string
  input_preview: string
}
```

```ts
// ToolUseStopPayload: tool_call_id → id
// ToolUseDeltaPayload: tool_call_id → id
// ToolResultPayload: tool_call_id → id, tool_name → name
```

（保留 snake_case，因为这是 wire format 的镜像。）

**前端渲染状态 `ToolUseBlock` 接口（第 99-111 行）**

```ts
// 改前
export interface ToolUseBlock {
  type: 'tool_use'
  index: number
  status: 'building' | 'calling' | 'success' | 'error'
  toolCallId: string
  toolName: string
  toolDisplayName: string
  inputPreview: string
  partialInputJson: string
  resultSummary: string | null
  resultData: unknown | null
  collapsed: boolean
}

// 改后（只改三个字段）
export interface ToolUseBlock {
  type: 'tool_use'
  index: number
  status: 'building' | 'calling' | 'success' | 'error'
  id: string                    // was toolCallId
  name: string                  // was toolName
  displayName: string           // was toolDisplayName
  inputPreview: string
  partialInputJson: string
  resultSummary: string | null
  resultData: unknown | null
  collapsed: boolean
}
```

---

### 3.3 前端 store `frontend/src/stores/chat.ts`

消费 SSE payload 的地方需要同步：

**`tool_use_start` case（第 144-163 行）**
```ts
// 改前
toolCallId: d.tool_call_id,
toolName: d.tool_name,
toolDisplayName: d.tool_display_name,
inputPreview: d.tool_input_preview,

// 改后
id: d.id,
name: d.name,
displayName: d.display_name,
inputPreview: d.input_preview,
```

**`loadConversation`（第 316-333 行附近，DB 回放构造 RenderBlock）**
```ts
// 改前
toolCallId: apiBlock.id,
toolName: apiBlock.name,
toolDisplayName: apiBlock.name,

// 改后
id: apiBlock.id,
name: apiBlock.name,
displayName: apiBlock.name,
```

（这里原本是把 DB 的 `id` / `name` 赋值给 `toolCallId` / `toolName`，改名后变成单纯赋值，命名一致。）

---

### 3.4 前端组件 `frontend/src/components/chat/components/blocks/ToolUseBlock.vue`

模板里引用 `block.toolDisplayName` 的地方（第 28 行）：
```vue
<!-- 改前 -->
<span class="...">{{ block.toolDisplayName }}</span>

<!-- 改后 -->
<span class="...">{{ block.displayName }}</span>
```

其他字段（`block.status`、`block.partialInputJson`、`block.resultData`）没有 `tool_` 前缀，不动。

---

## 4. 不在本次范围内（明确排除）

以下事项**本次不做**，遇到请保持原样：

1. `TOOL_DISPLAY_NAMES` 字典的位置（属于 Phase E）
2. `loadConversation` 和 `sendMessage` 之间的代码重复（属于 Phase C）
3. `switch(event)` 的结构（属于 Phase D）
4. `tool_use_start` 等专属事件是否并入 `content_block_*`（属于 Phase F）
5. `ToolUseBlock.vue` 的 `inputJsonText` / `resultText` 的 computed 逻辑
6. `chat_service.py` 的任何 `tool_call_id=` / `tool_name=` 构造器参数（PydanticAI API）
7. DB migration（不需要，DB 格式已经是 Anthropic 命名）
8. 任何 UI 样式 / Tailwind class

---

## 5. 验证步骤

完成改动后，请逐项确认：

### 5.1 静态检查

- [ ] 前端：`cd frontend && npx tsc --noEmit` 无新报错
- [ ] 后端：运行 `uv run ruff check backend/app/api/v1/chat/stream.py` 无新报错

### 5.2 全局搜索确认

用 grep 在前后端分别执行，确认没有遗漏：

```bash
# 前端不应再有 tool_call_id / tool_name / tool_display_name / tool_input_preview
grep -rn "tool_call_id\|tool_name\|tool_display_name\|tool_input_preview" frontend/src

# 前端不应再有 toolCallId / toolName / toolDisplayName（除了 CHANGELOG 类文件）
grep -rn "toolCallId\|toolName\|toolDisplayName" frontend/src

# 后端在 stream.py 的 SSE payload 里不应再有 tool_call_id / tool_name / tool_display_name / tool_input_preview
# （但 chat_service.py 的 ToolCallPart(tool_call_id=..., tool_name=...) 保留，那是 PydanticAI API）
grep -n "tool_call_id\|tool_name\|tool_display_name\|tool_input_preview" backend/app/api/v1/chat/stream.py
```

### 5.3 运行时自测

启动前后端，开一个新对话：

- [ ] 输入会触发 `search_notes` 工具的问题（例如："帮我查下我以前写过 Vue 的笔记"）
- [ ] 观察 tool_use 气泡正常展示工具名 / 展开/折叠 / 参数 / 结果
- [ ] 流式期间状态图标（spinner → wrench / xcircle）切换正常
- [ ] 刷新页面（触发 `loadConversation` 回放），历史 tool_use 仍然正常显示
- [ ] 浏览器 DevTools Network 面板看 `/chat/send` 的 SSE 流，payload 字段应为 `id` / `name` / `display_name` / `input_preview`（不再有 `tool_` 前缀）

---

## 6. 预期 diff 规模

- `backend/app/api/v1/chat/stream.py`：~15 行字符串替换
- `frontend/src/types/chat.ts`：~10 行字段改名
- `frontend/src/stores/chat.ts`：~8 行字段改名
- `frontend/src/components/chat/components/blocks/ToolUseBlock.vue`：1 行

**总计约 35 行改动，分布在 4 个文件。纯重命名，零逻辑变化。**

如果你的 diff 规模明显超过这个数量，说明你可能做了不该做的事，停下来检查。

---

## 7. 完成后

在报告里给出：
- 修改的文件清单（带行数）
- `grep` 验证命令的输出（应为空或只剩 PydanticAI 框架使用）
- 运行时自测结果（上述 5.3 的每一项）

**不要自动 commit**，让用户 review 后决定是否提交。
