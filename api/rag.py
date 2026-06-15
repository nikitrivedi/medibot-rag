import re

from groq import Groq

from chunker.medichunker import DEPARTMENT_ACCESS
from chunker.retriever import hybrid_search
from chunker.reranker import retrieve_and_rerank
from sql_rag.sql_rag import GROQ_MODEL, SQL_RAG_ROLES, sql_rag_answer

VALID_ROLES = {"billing_executive", "doctor", "nurse", "technician", "admin"}

ROLE_LABELS = {
    "billing_executive": "billing executive",
    "doctor": "doctor",
    "nurse": "nurse",
    "technician": "technician",
    "admin": "admin",
}

# Cross-encoder scores on contextualized_text are often negative for domain chunks.
RELEVANCE_THRESHOLD = -5.0

ANALYTICAL_PATTERN = re.compile(
    r"\b("
    r"how many|how much|count|total|number of|average|avg|sum|mean|"
    r"maximum|max|minimum|min|list all|top \d+|amount|rate|percentage|"
    r"pending claims|open tickets|per insurer|per department"
    r")\b",
    re.IGNORECASE,
)


def is_analytical(question: str) -> bool:
    return bool(ANALYTICAL_PATTERN.search(question))


def accessible_collections(role: str) -> list[str]:
    return [name for name, roles in DEPARTMENT_ACCESS.items() if role in roles]


def access_denied_message(role: str, blocked_collection: str | None = None) -> str:
    role_label = ROLE_LABELS.get(role, role)
    allowed = ", ".join(accessible_collections(role))
    if blocked_collection:
        return (
            f"As a {role_label}, you don't have access to the {blocked_collection} "
            f"documents. I can only answer from {allowed} collections."
        )
    return (
        f"As a {role_label}, I couldn't find relevant information in your accessible "
        f"documents. I can only answer from {allowed} collections."
    )


def _blocked_collection(question: str, role: str) -> str | None:
    unfiltered = hybrid_search(question, role=None, top_k=1)
    if not unfiltered:
        return None
    top_collection = unfiltered[0]["collection"]
    if top_collection in accessible_collections(role):
        return None
    return top_collection


def _is_access_denied(chunks: list[dict], question: str, role: str) -> bool:
    if not chunks:
        return True
    if all(chunk["rerank_score"] < RELEVANCE_THRESHOLD for chunk in chunks):
        return _blocked_collection(question, role) is not None
    return False


# Function to answer the user's question using the document RAG
def document_rag_answer(question: str, role: str) -> dict:
    chunks = retrieve_and_rerank(question, role)
    if _is_access_denied(chunks, question, role):
        blocked = _blocked_collection(question, role)
        return {
            "answer": access_denied_message(role, blocked),
            "sources": [],
        }

    context_parts = []
    sources = []
    for chunk in chunks:
        context_parts.append(
            f"[{chunk['source_document']} | {chunk['section_title']}]\n{chunk['text']}"
        )
        sources.append({
            "type": "document",
            "source_document": chunk["source_document"],
            "section_title": chunk["section_title"],
            "collection": chunk["collection"],
            "rerank_score": chunk["rerank_score"],
            "text": chunk["text"],
        })

    client = Groq()
    answer = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a MediAssist hospital assistant. "
                    "Answer using only the provided context. "
                    "Give a clear, practical answer with enough detail that is useful"
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n\n{chr(10).join(context_parts)}\n\nQuestion: {question}",
            },
        ],
        temperature=0,
    ).choices[0].message.content

    return {"answer": answer, "sources": sources}

# Main function to answer the user's question
def chat_answer(question: str, role: str) -> dict:
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}")

    use_sql = is_analytical(question) and role in SQL_RAG_ROLES
    if use_sql:
        result = sql_rag_answer(question)
        return {
            "answer": result["answer"],
            "retrieval_type": "SQL RAG",
            "role": role,
            "sources": [{
                "type": "sql",
                "sql": result["sql"],
                "results": result["results"],
            }],
        }

    result = document_rag_answer(question, role)
    return {
        "answer": result["answer"],
        "retrieval_type": "hybrid RAG",
        "role": role,
        "sources": result["sources"],
    }
