import { post } from '@/request'
import type { Ref } from 'vue'

export interface RunIngestionRequest {
  workflow_key: string // 默认 'conversation_to_note'
  source_type: 'internal' | 'pasted' | 'link'
  source_ref: string // internal 模式下传 conversation.uuid
  source_input?: string
  paste_format?: string // 'generic' | 'json'，internal 模式无意义
}

export interface NoteOutline {
  title: string
  summary: string
  tags: string[]
}

export type IngestionRunStatus =
  | 'pending'
  | 'running'
  | 'awaiting_user'
  | 'cancelling'
  | 'cancelled'
  | 'succeeded'
  | 'failed'

export interface RunIngestionResult {
  run_uuid: string
  status: IngestionRunStatus
  note_uuid: string | null
  draft: string
  outline: NoteOutline | null
}

const runFromConversation = (conversationUuid: string, loading?: Ref<boolean>) =>
  post(
    '/ingestion/run',
    {
      workflow_key: 'conversation_to_note',
      source_type: 'internal',
      source_ref: conversationUuid,
    } satisfies RunIngestionRequest,
    undefined,
    loading,
  )

export default { runFromConversation }
