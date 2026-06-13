from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc.document import CodeItem, SectionHeaderItem, TableItem, TitleItem

from chunker.models import MediChunk

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEPARTMENT_ACCESS = {
    "billing": ["billing_executive", "admin"],
    "clinical": ["doctor", "admin"],
    "nursing": ["nurse", "doctor", "admin"],
    "equipment": ["technician", "admin"],
    "general": ["billing_executive", "doctor", "nurse", "admin", "technician"],
}
FILE_PATHS = [
    Path("data/billing/billing_codes.pdf"),
    Path("data/billing/claim_submission_guide.md"),
    Path("data/clinical/diagnostic_reference.pdf"),
    Path("data/clinical/drug_formulary.pdf"),
    Path("data/clinical/treatment_protocols.pdf"),
    Path("data/nursing/icu_nursing_procedures.pdf"),
    Path("data/nursing/infection_control.pdf"),
    Path("data/equipment/equipment_manual.pdf"),
    Path("data/general/code_of_conduct.pdf"),
    Path("data/general/leave_policy.pdf"),
    Path("data/general/general_faqs.pdf"),
    Path("data/general/staff_handbook.pdf"),
]


def build_chunker() -> HybridChunker:
    tokenizer = HuggingFaceTokenizer.from_pretrained(model_name=EMBEDDING_MODEL)
    return HybridChunker(tokenizer=tokenizer)


def _chunk_type(doc_items) -> str:
    if any(isinstance(item, TableItem) for item in doc_items):
        return "table"
    if any(isinstance(item, CodeItem) for item in doc_items):
        return "code"
    if any(isinstance(item, TitleItem | SectionHeaderItem) for item in doc_items):
        return "heading"
    return "text"


# Convert a file to a list of MediChunks using Docling and chunker
def convert_file(path: Path | str, root: Path | None = None) -> list[MediChunk]:
    path = Path(path)
    root = root or Path.cwd()

    source_document = (
        str(path.relative_to(root)) if path.is_relative_to(root) else path.as_posix()
    )
    parts = source_document.split("/")
    collection = parts[1] if parts[0] == "data" else parts[0]
    access_roles = DEPARTMENT_ACCESS[collection]

    result = DocumentConverter().convert(path) # convert the file to a structured Docling document object
    if result.status != ConversionStatus.SUCCESS:
        raise ValueError(f"Could not convert {source_document}: {result.status}")

    # split the document into chunks
    chunker = build_chunker()
    chunks = []
    for i, chunk in enumerate(chunker.chunk(result.document)): # chunk the document into chunks
        chunks.append(
            MediChunk(
                chunk_id=f"{source_document}:{i}", # unique identifier for the chunk
                text=chunk.text,
                contextualized_text=chunker.contextualize(chunk),
                section_title=list(chunk.meta.headings or []), # list of section titles in the chunk
                collection=collection, # collection of the chunk
                access_roles=access_roles, # access roles for the chunk
                source_document=source_document, # source document of the chunk
                chunk_type=_chunk_type(chunk.meta.doc_items), # type of the chunk
                chunk_index=i, # index of the chunk
            )
        )
    return chunks
