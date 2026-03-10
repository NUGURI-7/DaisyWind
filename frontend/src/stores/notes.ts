import { defineStore } from "pinia";

import { ref } from "vue";
import noteApi from '@/api/note'
import type { Note, NoteDetail } from '@/api/note'

type NoteEntry = Note & { content?: string }
type SavingState = 'idle' | 'saving' | 'saved' | 'error'

export const useNoteStore = defineStore('notes', () => {
  const notesById = ref<Record<string,NoteEntry>>({})  
  const orderedIds = ref<string[]>([])
  const selectedId = ref<string | null>(null)
  const saving = ref<SavingState>('idle')

  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  let pendingSave: { uuid: string; content: string} | null = null
  let saveVersion = 0


  async function fetchList() {
    const res = await noteApi.getList()
    
    const notes: Note[] = res.data
    notesById.value = {}
    orderedIds.value = []
    for (const note of notes) {
      notesById.value[note.uuid] = { ...note }
      orderedIds.value.push(note.uuid)
    }
  }

  async function fetchOne(uuid:string) {
    const res = await noteApi.getOne(uuid)
    const detail: NoteDetail = res.data
    notesById.value[uuid] = {...notesById.value[uuid], ...detail}
    
  }

 async function create() {
   await flush()
   
   const res = await noteApi.createNote()
   const note: NoteDetail = res.data
   notesById.value[note.uuid] = {...note}
   orderedIds.value.unshift(note.uuid)
   selectedId.value = note.uuid
 }

  
  async function save(uuid:string,content: string) {
    pendingSave = { uuid, content }
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      _dosave(uuid, content)
      pendingSave = null
      debounceTimer = null
    }, 1000)
  }

  async function flush() {
    if (!pendingSave) return
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }

    const { uuid, content } = pendingSave
    pendingSave = null
    await _dosave(uuid, content)

  }

  async function _dosave(uuid:string, content: string) {
    const version = ++saveVersion
    saving.value = 'saving'
    try {
      const res = await noteApi.updateNote(uuid, content)
      if (version !== saveVersion) return
      const updated: NoteDetail = res.data
      notesById.value[uuid] = { ...notesById.value[uuid], ...updated }
      saving.value = 'saved'
    } catch {
      if (version === saveVersion) saving.value = 'error'
    }
  }


  async function remove(uuid: string) {

    if (pendingSave?.uuid === uuid) {
      if (debounceTimer) {
        clearTimeout(debounceTimer)
        debounceTimer = null
      }
      pendingSave = null
    }

    await noteApi.deleteNote(uuid)
    delete notesById.value[uuid]
    const idx = orderedIds.value.indexOf(uuid)
    
    if (idx !== -1) orderedIds.value.splice(idx,1)
    
    if (selectedId.value === uuid) {
      selectedId.value = orderedIds.value[0] ?? null
    }
  }
  
  
  return {
      notesById, orderedIds, selectedId, saving, fetchList, fetchOne, create, save, flush, remove
    }
  }




)