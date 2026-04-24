import type { ChatMessage, AssistantMessage } from '@/types/chat'

/**
 * 从 AssistantMessage 的 blocks 数组里拼出可复制的 Markdown 源文
 * - text block: 直接取 content
 * - tool_use block: 加一行注释，标明调用了什么工具；本步骤只做最简形式
 */
function assistantBlocksToMarkdown(msg: AssistantMessage): string {
  const parts: string[] = []

  for (const block of msg.blocks) {
    if (block.type === 'text') {
      parts.push(block.content)
    } else if (block.type === 'tool_use') {
      // 占位：先用一个注释行表示工具调用，后续可扩展
      parts.push(`> [调用工具: ${block.name}]`)
    }
  }

  return parts.join('\n\n').trim()
}

/**
 * 通用入口：给任意 ChatMessage，返回它的原始 Markdown 文本
 * MessageActions 组件的 content prop 直接吃这个函数的返回值
 */
export function getMessageMarkdown(msg: ChatMessage): string {
  if (msg.role === 'user') {
    return msg.content
  }
  return assistantBlocksToMarkdown(msg)
}
