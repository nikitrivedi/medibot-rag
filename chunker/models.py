from pydantic import BaseModel


class MediChunk(BaseModel):
    chunk_id: str
    text: str
    contextualized_text: str
    section_title: list[str]
    collection: str
    access_roles: list[str]
    source_document: str
    chunk_type: str
    chunk_index: int
