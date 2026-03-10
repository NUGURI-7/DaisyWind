# Notes Module Plan

> **Status: P1 Completed (2026-03-10)**

## Positioning

This document is a working implementation plan for the Notes module.
It is intended to guide development, not to freeze the design permanently.
If implementation reveals better tradeoffs, the plan can be adjusted.

## Notes Module Design

### 1. Backend Data Model

```text
Note
├── id (UUID)
├── user (FK -> User)
├── content (text, default "")
├── title (varchar 255, default "Untitled")   <- derived from content on backend
├── preview (varchar 100, default "")         <- derived from content on backend
├── deleted_at (datetime, null)               <- soft delete marker
├── created_at
└── updated_at
```

`title` extraction rule:
- Use the first Markdown `# H1` heading from `content`
- Fallback to `"Untitled"` when missing

`preview` extraction rule:
- Use the first non-heading body paragraph from `content`
- Truncate to the first 100 characters

### 2. API

| Method | Path | Description |
|---|---|---|
| `GET` | `/list` | Return note list metadata only, ordered by `updated_at` desc, excluding soft-deleted notes |
| `POST` | `/create` | Create a note immediately and return the full note |
| `GET` | `/{uuid}` | Return one note with full content |
| `PUT` | `/{uuid}` | Update note content only; backend derives `title` and `preview` |
| `DELETE` | `/{uuid}` | Soft delete by writing `deleted_at` |

> **Implementation note:** Path changed from `/notes` / `/notes/{id}` to `/list`, `/create`, `/{uuid}` to avoid FastAPI trailing slash redirect conflict with empty-string router paths.

All endpoints require authentication and are scoped to the current user only.

### 3. Frontend Store

File:
- `frontend/src/stores/notes.ts`

State:

```ts
notesById: Record<string, Note>
orderedIds: string[]
selectedId: string | null
saving: 'idle' | 'saving' | 'saved' | 'error'
```

Actions:
- `fetchList()` -> fetch metadata list and populate `notesById` + `orderedIds`
- `fetchOne(id)` -> fetch full content and merge into `notesById[id]`
- `create()` -> create note and prepend id into `orderedIds`
- `save(id, content)` -> save note content with 1s debounce
- `remove(id)` -> soft delete note and remove id from `orderedIds`

### 4. Frontend View Changes

Target file:
- `frontend/src/views/notes/index.vue`

Changes:
- Remove local state and local CRUD logic
- Use the Pinia store as the source of truth
- When selecting a note, call `fetchOne(id)` and initialize the editor after content is available
- Editor `onChange` triggers debounce 1s -> `store.save()`
- Flush the current pending save before switching notes to avoid losing the latest edit
- Top toolbar shows note title, delete button, and save state
- Delete flow uses DaisyUI modal confirm -> `store.remove()` -> auto-select first remaining note

### 5. Create Behavior

New notes should be persisted immediately.

Instead of creating a truly blank document, initialize new note content as:

```md
# Untitled
```

This keeps `content` as the single source of truth while allowing backend-derived `title` and `preview` to remain consistent.

### 6. Delivery Order

Backend:
1. Define `Note` model
2. Add Aerich migration
3. Implement `NoteService`, including `title` / `preview` extraction
4. Add 5 note endpoints and register the router

Frontend:
5. Add Pinia store `notes.ts`
6. Refactor `views/notes/index.vue` to use store, lazy loading, debounced autosave, and delete flow

### 7. Phase Two

> **Status: Not yet implemented.** Currently images are embedded as base64 data URIs directly in note content.

- Add image upload endpoint
- Store note images on local disk
- Serve images with cookie-auth-aware access control
- Integrate Crepe `uploadImage` callback

## Review Notes

The current design is solid enough to implement, with a few points that should remain explicit during development:

1. Avoid state split. `notesById` plus `orderedIds` is the correct direction, and list/detail data should keep merging into the same note entity instead of creating a separate content source.
2. Distinguish between metadata-loaded notes and content-loaded notes. A note in `notesById` may not yet contain full content, so the implementation should make that state explicit.
3. Soft delete is the right choice, but list queries should be backed by proper indexing for the common access pattern: current user's non-deleted notes ordered by `updated_at`.
4. Autosave needs ordering protection. If multiple save requests overlap, only the latest response should be allowed to win.
5. Creating a new note should be treated like a context switch: flush any pending save before creating and selecting the new note.

## Implementation Reminder

This plan is intentionally not treated as a rigid one-to-one build script.
If better production-grade tradeoffs appear during implementation, update this document and adjust the module design accordingly.
