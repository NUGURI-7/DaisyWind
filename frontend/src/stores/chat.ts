import { defineStore } from 'pinia'
import { ref } from 'vue'
import { streamChat } from '@/api/chat'
import type {
  AssistantMessage,
  TextBlock,
  MessageDeltaPayload,
  MessageStartPayload,
  ContentBlockDeltaPayload,
  ContentBlockStartPayload,
  ContentBlockStopPayload,
  SSEErrorPayload,
  ChatMessage,
} from '@/types/chat'

import {
  listConversations as apiListConversations,
  getConversationDetail,
  deleteConversation as apiDeleteConversation,
  type ConversationSummary,
} from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // 当前对话的消息列表（user + assistant 交替）
  const messages = ref<ChatMessage[]>([])

  // 当前正在流式输出的 assistant message
  const streaming = ref<AssistantMessage | null>(null)

  // 是否正在等待回复
  const isLoading = ref(false)

  // 对话列表（侧栏用）
  const conversations = ref<ConversationSummary[]>([])

  // 当前选中的对话 uuid
  const currentConversationUuid = ref<string | null>(null)

  // 加载对话详情时的 loading
  const isLoadingConversation = ref(false)

  /**
   * 发送消息并消费 SSE 事件流。
   */
  async function sendMessage(params: {
    message_uuid: string
    content: string
    provider: string
    model: string
  }) {
    // 确保有 currentConversationUuid（首次进入时为 null，临时生成一个）
    if (!currentConversationUuid) newConversation()

    const conversationUuid = currentConversationUuid.value!

    // 记录这次是否是"新对话"——用于发送完成后决定是否刷新侧栏
    const isNewConversation = !conversations.value.some((c: any) => c.uuid === conversationUuid)

    const userMessageUuid = crypto.randomUUID()

    // 先把 user message 加到列表里（乐观渲染）
    messages.value.push({ role: 'user', uuid: userMessageUuid, content: params.content })
    isLoading.value = true

    try {
      // 消费异步迭代器
      for await (const { event, data } of streamChat({
        conversation_uuid: conversationUuid,
        message_uuid: params.message_uuid,
        content: params.content,
        provider: params.provider,
        model: params.model,
      })) {
        const payload = JSON.parse(data)

        switch (event) {
          case 'message_start': {
            const d = payload as MessageStartPayload
            const msg: AssistantMessage = {
              role: 'assistant',
              uuid: d.message_uuid,
              model: d.model,
              provider: d.provider,
              status: 'streaming',
              blocks: [],
              usage: null,
              stopReason: null,
              errorMessage: null,
            }
            streaming.value = msg
            messages.value.push(msg)
            break
          }

          case 'content_block_start': {
            const d = payload as ContentBlockStartPayload
            if (d.type === 'text' && streaming.value) {
              const block: TextBlock = {
                type: 'text',
                index: d.index,
                status: 'active',
                content: '',
              }
              streaming.value.blocks.push(block)
            }
            break
          }

          case 'content_block_delta': {
            const d = payload as ContentBlockDeltaPayload
            if (streaming.value) {
              const block = streaming.value.blocks.find((b) => b.index === d.index)
              if (block && block.type === 'text') {
                block.content += d.text
              }
            }
            break
          }

          case 'content_block_stop': {
            const d = payload as ContentBlockStopPayload
            if (streaming.value) {
              const block = streaming.value.blocks.find((b) => b.index === d.index)
              if (block) {
                block.status = 'done'
              }
            }
            break
          }

          case 'message_delta': {
            const d = payload as MessageDeltaPayload
            if (streaming.value) {
              streaming.value.usage = d.usage
              streaming.value.stopReason = d.stop_reason
            }
            break
          }

          case 'message_stop': {
            if (streaming.value) {
              streaming.value.status = 'completed'
              streaming.value = null
            }
            break
          }

          case 'error': {
            const d = payload as SSEErrorPayload
            if (streaming.value) {
              streaming.value.status = 'error'
              streaming.value.errorMessage = d.message
              streaming.value = null
            }
            break
          }
        }
      }
    } catch (e: any) {
      // 网络错误（fetch 本身失败）
      if (streaming.value) {
        streaming.value.status = 'error'
        streaming.value.errorMessage = e.message || 'connect error'
        streaming.value = null
      }
    } finally {
      isLoading.value = false

      // 首次对话：流结束后(已入库)刷新侧栏，让新对话出现在列表里
      if (isNewConversation) {
        loadConversations().catch(() => {
          // 刷新失败不影响主流程，静默处理
        })
      }
    }
  }

  /**
   * 拉取当前用户的对话列表，填充侧栏。
   */
  async function loadConversations() {
    const res = await apiListConversations()
    conversations.value = res.data as ConversationSummary[]
  }

  /**
   * 加载指定对话的完整历史（含消息），切换为当前对话。
   */
  async function loadConversation(uuid: string) {
    isLoadingConversation.value = true
    try {
      const res = await getConversationDetail(uuid)
      const detail = res.data

      currentConversationUuid.value = uuid

      // 后端扁平 messages → 前端渲染结构
      messages.value = detail.messages.map((msg: any): ChatMessage => {
        if (msg.role === 'user') {
          return {
            role: 'user',
            uuid: msg.uuid,
            content: msg.content,
          }
        }

        return {
          role: 'assistant',
          uuid: msg.uuid,
          model: detail.model,
          provider: detail.provider,
          status: 'completed',
          blocks: [{ type: 'text', index: 0, status: 'done', content: msg.content }],
          usage: null,
          stopReason: null,
          errorMessage: null,
        }
      })

      streaming.value = null
    } finally {
      isLoadingConversation.value = false
    }
  }

  /**
   * 开始一个新对话：清空消息，生成新的 uuid。
   * 注意：此时 uuid 还没在后端存在，要等第一次 sendMessage 触发后端 get_or_create 才会落库。
   */
  function newConversation() {
    messages.value = []
    streaming.value = null
    currentConversationUuid.value = crypto.randomUUID()
  }

  /**
   * 删除一条对话。如果删的是当前对话，自动切到新对话状态。
   */
  async function removeConversation(uuid: string) {
    await apiDeleteConversation(uuid)

    conversations.value = conversations.value.filter((c: any) => c.uuid !== uuid)

    if (currentConversationUuid.value === uuid) {
      newConversation()
    }
  }

  return {
    messages,
    streaming,
    isLoading,
    conversations,
    currentConversationUuid,
    isLoadingConversation,
    loadConversation,
    newConversation,
    removeConversation,
    loadConversations,
    sendMessage,
  }
})
