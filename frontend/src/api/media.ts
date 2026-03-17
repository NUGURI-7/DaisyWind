import { post } from '@/request'
import type { Ref } from 'vue'

export interface PresignedUrlResponse {
  upload_url: string
  public_url: string
  object_name: string
}

export const getPresignedUrl = (filenmae: string, contentType: string, loading?: Ref<boolean>) =>
  post('/media/presigned-url', { filenmae, content_type: contentType }, undefined, loading)

export default { getPresignedUrl }
