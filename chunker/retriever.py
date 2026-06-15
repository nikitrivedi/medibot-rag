"""Step 2: Hybrid retrieval — dense + BM25 in one Qdrant query."""

from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchAny,
    Prefetch,
    SparseVector,
)
from sentence_transformers import SentenceTransformer

from chunker.ingest import (
    DENSE_VECTOR,
    EMBEDDING_MODEL,
    QDRANT_COLLECTION,
    QDRANT_URL,
    SPARSE_MODEL,
    SPARSE_VECTOR,
)

PREFETCH_LIMIT = 20


def hybrid_search(query: str, role: str | None = None, top_k: int = 10) -> list[dict]:
    # Step 1 — Turn the user question into a dense vector (semantic)
    dense_model = SentenceTransformer(EMBEDDING_MODEL)
    dense_vector = dense_model.encode(query).tolist()

    # Step 2 — Turn the user question into a sparse vector (keywords / BM25)
    sparse_model = SparseTextEmbedding(SPARSE_MODEL)
    sparse = list(sparse_model.embed([query]))[0]
    sparse_vector = SparseVector(
        indices=sparse.indices.tolist(),
        values=sparse.values.tolist(),
    )

    # Step 3 — Only return chunks this role is allowed to see
    query_filter = None
    if role:
        query_filter = Filter(
            must=[FieldCondition(key="access_roles", match=MatchAny(any=[role]))]
        )

    # Step 4 — One Qdrant call: search dense + sparse, fuse with RRF
    # Dense rank is computed by the cosine similarity search on the dense vector. 
    # Sparse rank is computed by the BM25 keyword search on the sparse vector.
    # Each prefetch runs its own similarity search and returns the top PREFETCH_LIMIT results sorted by the similarity score or BM25 score.
    # RRF is the rank fusion algorithm that combines the dense and sparse ranks. A chunk that ranks high in both dense and sparse search is more likely to be relevant to the query.
    # The final result is the top top_k results from the fusion of the dense and sparse ranks.
    client = QdrantClient(url=QDRANT_URL)
    response = client.query_points(
        collection_name=QDRANT_COLLECTION,
        prefetch=[
            Prefetch(query=dense_vector, using=DENSE_VECTOR, limit=PREFETCH_LIMIT),
            Prefetch(query=sparse_vector, using=SPARSE_VECTOR, limit=PREFETCH_LIMIT),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        query_filter=query_filter,
        limit=top_k,
    )

    results = []
    for point in response.points:
        results.append({
            "score": point.score,
            "text": point.payload.get("text"),
            "contextualized_text": point.payload.get("contextualized_text"),
            "source_document": point.payload.get("source_document"),
            "section_title": point.payload.get("section_title"),
            "collection": point.payload.get("collection"),
            "chunk_type": point.payload.get("chunk_type"),
            "access_roles": point.payload.get("access_roles"),
        })
    return results


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "cashless pre-auth SLA"
    role = sys.argv[2] if len(sys.argv) > 2 else "billing_executive"

    for r in hybrid_search(query, role):
        print(f"[{r['score']:.4f}] {r['source_document']}")
        print(f"  {r['text'][:120]}...")
        print()
