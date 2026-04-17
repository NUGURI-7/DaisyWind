// ==================== SSE 事件 Payload ====================

export interface MessageStartPayload {
  conversation_uuid: string
  message_uuid: string
  model: string
  provider: string
}

export interface ContentBlockStartPayload {
  index: number
  type: 'text' // P1 加 'thinking'
}

export interface ContentBlockDeltaPayload {
  index: number
  type: 'text_delta'
  text: string
}

export interface ContentBlockStopPayload {
  index: number
}

export interface UsageInfo {
  input_tokens: number
  output_tokens: number
  cost: number | null
}

export interface MessageDeltaPayload {
  stop_reason: 'end_turn' | 'max_tokens' | 'cancelled'
  usage: UsageInfo
}

export interface SSEErrorPayload {
  code: string
  message: string
}

// ==================== 前端渲染状态 ====================

export interface TextBlock {
  type: 'text'
  index: number
  status: 'active' | 'done'
  content: string
}

// P1 再加 ThinkingBlock / ToolUseBlock
export type RenderBlock = TextBlock

export interface AssistantMessage {
  role: 'assistant'
  uuid: string
  model: string
  provider: string
  status: 'streaming' | 'completed' | 'error'
  blocks: RenderBlock[]
  usage: UsageInfo | null
  stopReason: string | null
  errorMessage: string | null
}

export interface UserMessage {
  role: 'user'
  uuid: string
  content: string
}

export type ChatMessage = UserMessage | AssistantMessage
