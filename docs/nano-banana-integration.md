# Nano Banana 图像生成接入方案

## 1. 目标

在现有 Gemini 文本对话基础上，接入 Google 的图像生成模型
（`gemini-3.1-flash-image-preview` / `gemini-3-pro-image-preview`），
让 AI 可以在对话流中直接生成图片，图片存储到 Cloudflare R2，
以 URL 形式返回前端渲染。

## 2. Spike 验证结论（已完成）

通过两轮 spike 确认：

| 关键事实 | 影响 |
|---|---|
| PydanticAI 1.70 通过 `FilePart(content=BinaryImage(...))` **原生透传** Gemini 图像输出 | 无需降级到 `google-genai` SDK |
| Agent 默认 `output_type=str` 会对纯图片输出触发 **RetryPrompt**，必须显式 `output_type=[str, BinaryImage]` | 关键配置点 |
| Gemini 返回 **JPEG 格式**，且是**已解码 bytes**（非 Base64） | 后端跳过 base64 解码，直接 `put_object` |
| 在 `run_stream_events` 层，图片作为**单个 `PartStartEvent`** 一次性到达，**无 Delta、无 PartEnd** | 无需 chunk 拼接；必须在 `PartStartEvent` 当场处理 |
| `FinalResultEvent` 在 image 场景也会触发 | 现有代码未处理此事件，暂不影响 |

### 为什么"流式拼接"无收益

底层 Gemini HTTP API 的 interleaved streaming 会把图片分多 chunk 发送（Open-WebUI 曾因此踩坑），
但 **PydanticAI 帮我们在事件层拼好了**。`BinaryImage.data` 到我们手里时已经是完整 bytes。
此外 R2 的 multipart upload 门槛是 5MB+，适合视频级文件；生成图片顶多 2MB，
**单次 `put_object` 就是最优路径**。

## 3. 架构决策

| 决策点 | 选择 | 理由 |
|---|---|---|
| 图像输出形式 | 融合式（对话流中返回 `BinaryImage`） | Gemini 原生能力 |
| 图片存储 | Cloudflare R2，后端直传 | 复用现有基础设施 |
| 上传接口 | 新增 `R2Storage.upload_bytes()` 同步方法 | 和现有预签名 URL 方法并列 |
| 异步包装 | 调用方 `asyncio.to_thread` | boto3 同步，不污染 event loop |
| 上传模式 | 单次 `put_object` | 图片 <5MB，multipart 无收益 |
| SSE 协议 | 单一 `image` 事件 + `status` 字段 | production-grade event schema |
| Agent 配置 | Gemini 所有模型统一 `output_type=[str, BinaryImage]` | 兼容文本+图像两种场景 |
| 计费 | 重构 `calc_cost` 支持按张计费 | 拒绝"假装 token"的 hack |
| Loading UI | `ldrs` **Trefoil** + "Generating image..."，占一行 | 和现有动画栈一致 |
| 对象命名 | `chat/generated/{user_id}/{uuid}.jpg` | 与 `notes/uploads/...` 路径语义对齐 |

## 4. SSE 事件协议

新增 `image` 事件类型，承载图片 block 的完整生命周期：

```
event: image
data: {
  "id": "img_<uuid>",
  "status": "loading" | "ready" | "error",
  "url"?:     string,  // status=ready 时存在
  "message"?: string   // status=error 时存在
}
```

前端通过 `id` 匹配占位 block，按 `status` 切换 UI 状态。

## 5. 改动清单

### 5.1 后端

#### `backend/app/core/storage.py`
新增方法：
```python
def upload_bytes(
    self,
    data: bytes,
    object_name: str,
    content_type: str = "application/octet-stream",
) -> str:
    """后端直传：上传二进制数据到 R2，返回 public URL。"""
```
- 内部调用 `self.s3_client.put_object(...)`
- `settings.R2_PUBLIC_URL` 为空时抛 `ValueError`
- 保持同步（boto3 本身同步），调用方负责 `asyncio.to_thread`
- 不加重试 / 不加日志

#### `backend/app/agents/chat_agent.py`（或 Agent 构造入口）
Gemini 系列模型统一设置：
```python
agent = Agent(model=..., output_type=[str, BinaryImage], ...)
```
非 Gemini 模型保持默认。

#### `backend/app/api/v1/chat/stream.py`
在现有 `PartStartEvent` 分支旁新增 `FilePart` 处理：
```
elif isinstance(event, PartStartEvent) and isinstance(event.part, FilePart):
    1. placeholder_id = f"img_{uuid4().hex}"
    2. object_name = f"chat/generated/{user_id}/{uuid4().hex}.jpg"
    3. blocks.append({
         "type": "image",
         "id": placeholder_id,
         "status": "loading",
         "url": None,
       })
    4. yield sse_event("image", {"id": placeholder_id, "status": "loading"})
    5. try:
           url = await asyncio.to_thread(
               r2_storage.upload_bytes,
               event.part.content.data,
               object_name,
               "image/jpeg",
           )
           blocks[-1]["status"] = "ready"
           blocks[-1]["url"] = url
           yield sse_event("image", {"id": placeholder_id, "status": "ready", "url": url})
       except Exception as e:
           blocks[-1]["status"] = "error"
           yield sse_event("image", {"id": placeholder_id, "status": "error", "message": str(e)})
```
**要点**：无 `PartEndEvent` 触发；必须在 `PartStartEvent` 内完成上传。

#### `backend/app/agents/pricing.py`
重构 `TOKEN_PRICE` 数据结构：
```python
{
    "text_input_per_million":  float,
    "text_output_per_million": float,
    "image_output_per_unit":   float,  # 可选，仅图像模型有
}
```
`calc_cost` 接口扩展支持 image 计数参数。

#### `backend/app/schemas/chat_schema.py`
新增 `ImageBlock` 类型：
```python
class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    id: str
    status: Literal["loading", "ready", "error"]
    url: str | None = None
```
历史消息加载时能正确反序列化。

### 5.2 前端

#### 新建 `frontend/src/components/chat/blocks/ImageBlock.vue`
- loading 状态：`<l-trefoil />` + "Generating image..."，占一行，居中
- ready 状态：`<img>` 带圆角、阴影，点击放大
- error 状态：错误图标 + 文案

#### chat message 渲染器
识别 `type: "image"` 的 block，交给 `ImageBlock.vue` 渲染。

#### SSE handler
- 订阅 `image` 事件类型
- 按 `id` 找到对应 block，更新其 `status` / `url` / `message`

#### `frontend/src/components/chat/components/MessageInput.vue`
`MODEL_OPTIONS` 新增：
- `gemini-3.1-flash-image-preview` → 标签 "Nano Banana 2"
- `gemini-3-pro-image-preview` → 标签 "Nano Banana Pro"
- （可选）`gemini-3.1-flash-lite-preview` → "Gemini 3.1 Flash-Lite"
- （可选）`gemini-3.1-pro-preview` → "Gemini 3.1 Pro"

## 6. 实施步骤

| Step | 内容 | 状态 |
|---|---|---|
| 1 | Spike 验证 PydanticAI 图像透传（iter + run_stream_events） | ✅ 完成 |
| 2 | `storage.py` 新增 `upload_bytes` | 👈 当前 |
| 3 | Agent 构造加 `output_type=[str, BinaryImage]` | |
| 4 | `chat_schema.py` 新增 `ImageBlock` 类型 | |
| 5 | `stream.py` 处理 `FilePart` + 上传 R2 + 发 `image` SSE | |
| 6 | `pricing.py` 重构支持图像计费 | |
| 7 | 前端新建 `ImageBlock.vue` | |
| 8 | 前端 SSE handler 处理 `image` 事件 | |
| 9 | 前端 `MODEL_OPTIONS` 加入 Nano Banana 模型 | |
| 10 | 端到端测试：loading / ready / error 三种路径 | |

## 7. 已知风险与后续

- **生产环境图片可访问性**：依赖 `R2_PUBLIC_URL` 已正确配置公开访问
- **极端情况**：模型一次响应可能生成多张图，目前设计已兼容（每个 `FilePart` 走一遍循环）
- **计费校准**：图片定价按分辨率分档，`pricing.py` 先按 "standard" 单档处理，后续再细化
- **落库 schema 迁移**：新增 `ImageBlock` 类型后，历史数据解析向下兼容（未出现 `type=image` 的旧数据不受影响）
