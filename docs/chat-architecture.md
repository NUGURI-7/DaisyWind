# Chat 模块架构设计文档

> 基于 2026-03-19 技术选型讨论整理，作为后续开发的唯一参考。

---

## 1. 技术选型结论

| 领域 | 选型 | 理由 |
|------|------|------|
| Agent 框架 | **PydanticAI** | 依赖注入（`RunContext[Deps]`）与 FastAPI 风格一致；原生多 Provider 支持；类型安全的结构化输出 |
| 多模型路由 | **PydanticAI 原生** | 内置支持 OpenAI / Anthropic / Gemini / DeepSeek / Qwen 等，无需自建路由层 |
| RAG 向量存储 | **pgvector**（复用 PostgreSQL） | 不引入额外依赖，单体部署友好 |
| Embedding | 可插拔（阿里 DashScope / OpenAI / Gemini / 本地） | 通过抽象类切换，默认待定 |
| 联网搜索 | **Tavily** | API 简洁，适合 Agent tool 调用 |
| 流式输出 | **SSE**（FastAPI StreamingResponse） | 单向推送足够，比 WebSocket 简单 |
| 异步任务队列 | **ARQ**（async Redis queue） | 与 FastAPI async 一致，轻量，已有 Redis |
| 代码沙箱 | **外置沙箱服务**（Docker API / Firecracker） | 安全隔离，后期实现 |

### 放弃的方案

| 方案 | 放弃原因 |
|------|----------|
| LangGraph | 概念过重（Graph/Node/State/Edge/Checkpoint），个人项目不需要复杂状态机 |
| LangChain | 抽象层太多，与 FastAPI 集成不自然 |
| OpenAI Agents SDK | 无依赖注入机制，Tool 访问外部依赖（DB/Redis/用户上下文）需 closure 或全局对象，写法不如 PydanticAI 干净；且名义上与 OpenAI 绑定，Provider 扩展不如 PydanticAI 原生 |
| LiteLLM | 需要独立 Proxy 进程，项目只能跑单体；PydanticAI 已原生支持多 Provider，不再需要 |

---

## 2. 目标 LLM Provider

PydanticAI 原生支持以下 Provider，通过 `model` 参数切换，无需手动管理 `base_url`：

| Provider | PydanticAI model 标识 | 备注 |
|----------|----------------------|------|
| DeepSeek | `openai:deepseek-chat`（自定义 base_url）| 默认 Provider |
| 阿里 Qwen (DashScope) | `openai:qwen-turbo`（自定义 base_url） | OpenAI 兼容模式 |
| OpenAI | `openai:gpt-4o-mini` | 原生支持 |
| Google Gemini | `google-gla:gemini-2.0-flash` | 原生支持 |
| Anthropic Claude | `anthropic:claude-sonnet-4-20250514` | 原生支持（PydanticAI 独有优势） |

---

## 3. 后端目录结构

```
backend/app/
│
├── agents/                        ← 新增：Agent 编排层
│   ├── __init__.py
│   ├── deps.py                    ← AgentDeps 依赖容器（DB/Redis/User 等）
│   ├── providers.py               ← Provider 配置 + 价格表 + model 工厂
│   ├── orchestrator.py            ← 主 Orchestrator Agent（意图判断 + 委派）
│   ├── research_agent.py          ← RAG + Notes 检索
│   ├── web_agent.py               ← Tavily 联网搜索
│   └── code_agent.py              ← 代码生成 + 外置沙箱调用
│
├── tools/                         ← 新增：Tool 定义层（@agent.tool）
│   ├── __init__.py
│   ├── notes_tool.py              ← 搜索/读取 Notes
│   ├── rag_tool.py                ← 向量检索
│   ├── web_search_tool.py         ← Tavily 搜索封装
│   └── code_tool.py               ← 调用外置沙箱 HTTP API
│
├── rag/                           ← 新增：RAG 基础设施
│   ├── __init__.py
│   ├── embeddings.py              ← EmbeddingProvider 抽象 + 各实现
│   ├── vector_store.py            ← pgvector 读写（相似度搜索）
│   └── indexer.py                 ← Notes → 向量库（增量 / 全量索引）
│
├── api/v1/
│   └── chat/                      ← 新增：Chat 路由
│       ├── __init__.py
│       └── chat.py                ← SSE 流式接口 + 对话 CRUD
│
├── models/
│   ├── chat_model.py              ← 已有：Conversation, ChatMessage（需改造）
│   └── rag_model.py               ← 新增：NoteEmbedding 向量表
│
├── schemas/
│   └── chat_schema.py             ← 已有（需扩展）
│
├── services/
│   └── chat_service.py            ← 已有（需扩展）
│
└── core/
    └── ...                        ← 已有基础设施
```

---

## 4. 核心设计详解

### 4.1 依赖容器（`agents/deps.py`）

PydanticAI 的核心优势——通过 `RunContext[Deps]` 将外部依赖类型安全地注入到 Agent 和 Tool 中：

```python
from dataclasses import dataclass
from backend.app.models import User, Conversation

@dataclass
class AgentDeps:
    """Agent 运行时依赖，注入到所有 Tool 中"""
    user: User                      # 当前用户
    conversation: Conversation      # 当前对话
    redis: Redis                    # Redis 连接（取消检测、缓存）
    # 后续可扩展：db_session, http_client 等
```

Tool 通过 `RunContext` 拿到依赖，无需全局变量或 closure：

```python
from pydantic_ai import RunContext

@orchestrator.tool
async def search_notes(ctx: RunContext[AgentDeps], query: str) -> str:
    user = ctx.deps.user  # 类型安全，IDE 自动补全
    notes = await Note.filter(user=user, content__icontains=query).all()
    return format_notes(notes)
```

### 4.2 Provider 管理（`agents/providers.py`）

```python
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.anthropic import AnthropicModel

def get_model(provider: str, model_name: str):
    """根据 provider 返回 PydanticAI Model 实例"""
    match provider:
        case "deepseek":
            return OpenAIModel(model_name, base_url="https://api.deepseek.com/v1", api_key=...)
        case "qwen":
            return OpenAIModel(model_name, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", api_key=...)
        case "openai":
            return OpenAIModel(model_name, api_key=...)
        case "gemini":
            return GeminiModel(model_name, api_key=...)
        case "anthropic":
            return AnthropicModel(model_name, api_key=...)

# Token 单价表（$/M tokens）
TOKEN_PRICE = {
    "deepseek-chat":        {"input": 0.27,  "output": 1.10},
    "deepseek-reasoner":    {"input": 0.55,  "output": 2.19},
    "qwen-turbo":           {"input": 0.30,  "output": 0.60},
    "gpt-4o-mini":          {"input": 0.15,  "output": 0.60},
    "gemini-2.0-flash":     {"input": 0.10,  "output": 0.40},
    "claude-sonnet-4-20250514": {"input": 3.00,  "output": 15.00},
}
```

### 4.3 Agent 分工

```
用户消息 → Orchestrator Agent
              │
              ├── 需要检索知识 → 委派 → ResearchAgent
              │                         ├── notes_tool（全文搜索 Notes）
              │                         └── rag_tool（向量相似度搜索）
              │
              ├── 需要联网     → 委派 → WebAgent
              │                         └── web_search_tool（Tavily API）
              │
              └── 需要写/跑代码 → 委派 → CodeAgent
                                        └── code_tool（调外置沙箱）
```

- **Orchestrator** 是唯一入口，负责意图判断和结果整合
- 简单对话由 Orchestrator 直接回复，不委派
- 各专项 Agent 完成任务后返回结果给 Orchestrator
- PydanticAI 中可通过 Tool 内调用子 Agent 实现委派（非 Agents SDK 的 Handoff 概念，但效果相同）

### 4.4 会话历史与 Context 管理

**持久化**：PydanticAI 本身无状态，持久化由 `chat_service` 负责。

**流程**：
1. 前端发送消息 → 后端从 DB 加载该对话的所有 `ChatMessage`
2. 组装成 `message_history` 传给 `agent.run()` 或 `agent.run_stream()`
3. Agent 响应完成后，将 user message 和 assistant response 写回 DB

**Context 超长处理 — 自动摘要压缩**：
- 当对话 token 数接近模型上下文窗口阈值时，触发摘要
- 用 LLM 将早期消息压缩为一条 summary
- `Conversation` 表新增 `summary` 字段，存储压缩后的摘要
- 下次组装 input 时：`[{role: "system", content: summary}, ...最近N条消息]`

### 4.5 多模态消息格式

`ChatMessage.content` 从纯文本改为 **JSON 多段结构**（兼容 OpenAI Vision API 格式）：

```json
[
  {"type": "text", "text": "帮我分析这张图"},
  {"type": "image_url", "image_url": {"url": "https://r2.example.com/xxx.png"}}
]
```

- 纯文本消息保持字符串，多模态消息使用 JSON 数组
- 图片先通过已有的 Media 模块上传到 R2，拿到 URL 后放入消息

### 4.6 SSE 流式输出（Claude 风格结构化事件）

模仿 Claude Web 端的 streaming 体验，定义以下 SSE 事件类型：

```
event: message_start
data: {"conversation_uuid": "...", "model": "deepseek-chat"}

event: content_block_start
data: {"type": "text", "index": 0}

event: content_block_delta
data: {"type": "text_delta", "text": "你好"}

event: content_block_stop
data: {"index": 0}

event: tool_use_start
data: {"tool_name": "web_search", "tool_input": {"query": "..."}}

event: tool_use_result
data: {"tool_name": "web_search", "result": "..."}

event: message_delta
data: {"stop_reason": "end_turn", "usage": {"input_tokens": 120, "output_tokens": 58, "cost": 0.0001}}

event: message_stop
data: {}

event: error
data: {"message": "..."}
```

前端根据 `event` 类型分别渲染：文本流、Tool 调用卡片、Token 用量等。

PydanticAI 通过 `agent.run_stream()` 返回 `StreamedRunResult`，消费其异步迭代器转换为上述 SSE 事件。

### 4.7 用户取消流式输出

1. SSE 流启动时，在 Redis 写入 `stream:cancel:{conversation_uuid}` = `0`
2. 前端点击「停止生成」→ 调用 `POST /chat/{uuid}/cancel`
3. 后端将 Redis key 设为 `1`
4. 流式循环中周期性检查该 key，检测到 `1` 则 break
5. 流正常结束后清除 Redis key

### 4.8 Embedding 抽象（`rag/embeddings.py`）

```python
class EmbeddingProvider(ABC):
    dim: int  # 向量维度

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

class OpenAIEmbedding(EmbeddingProvider):     # text-embedding-3-small, dim=1536
class QwenEmbedding(EmbeddingProvider):       # text-embedding-v3, dim=1024
class GeminiEmbedding(EmbeddingProvider):     # embedding-001, dim=768
class LocalEmbedding(EmbeddingProvider):      # sentence-transformers (HTTP)
```

- 配置决定使用哪个实现
- `NoteEmbedding` 表记录 `provider` 和 `dim`，切换 Provider 时需全量重建索引

### 4.9 Notes 异步索引（ARQ + Redis）

- Note 新增/更新时，通过 ARQ 派发异步任务
- 任务内容：分块 → Embedding → 写入 pgvector
- 不阻塞主请求，索引失败可重试

### 4.10 Token 计费追踪

- 每次 Agent 响应完成后，从 `result.usage()` 读取 token 数（PydanticAI 内置）
- 查 `TOKEN_PRICE` 表计算费用
- 写入 `ChatMessage.token_count` 和 `cost` 字段
- 后续可聚合为用户级别的用量统计

---

## 5. 数据模型改动

### 5.1 `Conversation`（已有，需扩展）

| 字段 | 类型 | 变化 |
|------|------|------|
| `summary` | `TextField(null=True)` | **新增**：自动摘要压缩内容 |
| `provider` | `CharField(max_length=20, default="deepseek")` | **新增**：当前使用的 Provider |

### 5.2 `ChatMessage`（已有，需改造）

| 字段 | 类型 | 变化 |
|------|------|------|
| `content` | `JSONField / TextField` | **改造**：支持多模态 JSON 格式 |
| `token_count` | `IntField(null=True)` | 已有 |
| `cost` | `DecimalField(null=True)` | **新增**：本条消息的费用 |
| `tool_calls` | `JSONField(null=True)` | **新增**：Tool 调用记录 |

### 5.3 `NoteEmbedding`（新增）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `BigIntField(pk=True)` | |
| `note` | `ForeignKey → Note` | |
| `chunk_index` | `IntField` | 分块序号 |
| `chunk_text` | `TextField` | 原文分块 |
| `embedding` | `vector(dim)` | pgvector 向量（维度由 Provider 决定） |
| `provider` | `CharField` | 生成该向量的 Embedding Provider |
| `dim` | `IntField` | 向量维度 |
| `created_at` | `DatetimeField` | |

---

## 6. API 端点设计

### Chat 路由（`/api/nuguri/v1/chat`）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/send` | 发送消息，返回 SSE 流（主接口） |
| `POST` | `/{uuid}/cancel` | 取消生成 |
| `GET` | `/conversations` | 对话列表 |
| `GET` | `/conversations/{uuid}` | 对话详情（含消息） |
| `DELETE` | `/conversations/{uuid}` | 删除对话 |
| `PATCH` | `/conversations/{uuid}` | 更新对话（标题、模型等） |

### `/send` 请求体

```json
{
  "conversation_uuid": "xxx-xxx",
  "content": [
    {"type": "text", "text": "分析这张图"},
    {"type": "image_url", "image_url": {"url": "https://..."}}
  ],
  "provider": "deepseek",
  "model": "deepseek-chat"
}
```

---

## 7. config.py 扩展

```python
# ==================== LLM Providers ====================
DEEPSEEK_API_KEY: str = ""
OPENAI_API_KEY: str = ""
DASHSCOPE_API_KEY: str = ""
GEMINI_API_KEY: str = ""
ANTHROPIC_API_KEY: str = ""          # PydanticAI 原生支持 Claude
DEFAULT_PROVIDER: str = "deepseek"
DEFAULT_MODEL: str = "deepseek-chat"

# ==================== Tavily ====================
TAVILY_API_KEY: str = ""

# ==================== Embedding ====================
EMBEDDING_PROVIDER: str = "qwen"
```

---

## 8. 新增依赖

```
pydantic-ai            # PydanticAI Agent 框架
tavily-python           # Tavily 联网搜索
asyncpg                 # pgvector 需要（Tortoise 已有）
pgvector                # pgvector Python 支持
arq                     # 异步 Redis 任务队列
```

> 注：PydanticAI 会自动引入 `openai`、`anthropic`、`google-generativeai` 等 SDK 作为可选依赖，按需安装。

---

## 9. 实施阶段（建议）

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| **P0** | Provider 管理 + 基础 Agent（无 Tool）+ SSE 流式 + 对话 CRUD | 🔴 当前重点 |
| **P1** | 多 Agent 委派 + Notes Tool + Tavily Tool | 🔴 当前重点 |
| **P2** | RAG（pgvector + Embedding + indexer） | 🔴 当前重点 |
| **P3** | 多模态输入（图片消息） | ⏸️ 后续考虑 |
| **P4** | Context 自动摘要压缩 | ⏸️ 后续考虑 |
| **P5** | Token 计费统计 UI | ⏸️ 后续考虑 |
| **P6** | 代码执行沙箱 | ⏸️ 后续考虑 |

> P0–P2 为当前阶段核心目标（AI 能力技术验证），P3–P6 待核心能力跑通后再按需推进。

---

## 10. 暂不考虑

- 对话分支（edit & branch）
- 对话标题自动生成（AI 生成）— 现有逻辑取前 30 字够用
- 用户级限流
- RAG 分块策略细节（P2 阶段再定）
