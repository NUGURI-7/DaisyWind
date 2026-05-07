# backend/app/schemas/ingestion_schema.py
from pydantic import BaseModel


class IngestionRequest(BaseModel):
    workflow_key: str = "conversation_to_note"
    source_type: str = "pasted"
    source_input: str
    source_ref: str
    paste_format: str = "generic"