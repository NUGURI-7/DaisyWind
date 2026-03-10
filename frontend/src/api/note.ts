import { get, post, put, del } from '@/request'
import type { Ref } from 'vue'


export interface Note {
  uuid: string
  title: string
  preview: string
  created_at: string
  updated_at: string
}

export interface NoteDetail extends Note {
  content: string
}

const getList = (loading?: Ref<boolean>) =>
  get('/note/list', undefined, loading)

const createNote = (loading?: Ref<boolean>) =>
  post('/note/create', undefined, undefined, loading)

const getOne = (uuid: string, loading?: Ref<boolean>) =>
  get(`/note/${uuid}`, undefined, loading)

const updateNote = (uuid: string, content: string, loading?: Ref<boolean>) =>
  put(`/note/${uuid}`, { content }, undefined, loading)

const deleteNote = (uuid: string, loading?: Ref<boolean>) =>
  del(`/note/${uuid}`, undefined, undefined, loading)

export default { getList, createNote, getOne, updateNote, deleteNote }