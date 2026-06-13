"""Step 1: Chunk documents and store dense + sparse vectors in Qdrant.

Dense  — contextualized_text + MiniLM (semantic search)
Sparse — text + BM25 (keyword / ICD / drug name search)

Step 2 retrieval: chunker/retriever.py
"""

import uuid
from pathlib import Path

from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    Modifier,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)
from sentence_transformers import SentenceTransformer

from chunker.medichunker import EMBEDDING_MODEL, FILE_PATHS, convert_file
from chunker.models import MediChunk

QDRANT_URL = "http://localhost:6333" # URL of the Qdrant server
QDRANT_COLLECTION = "medibot_hybrid" # name of the Qdrant collection
DENSE_VECTOR = "dense" # dense vector for semantic search
SPARSE_VECTOR = "sparse" # sparse vector for keyword search
SPARSE_MODEL = "Qdrant/bm25" # BM25 model for sparse vector search
VECTOR_SIZE = 384 # size of the dense vector


# Convert all documents to chunks
def convert_all_documents(root: Path = Path(".")) -> list[MediChunk]:
    chunks = []
    for path in FILE_PATHS:
        try:
            chunks.extend(convert_file(path, root=root))
        except Exception as e:
            print(f"Skipped {path}: {e}")
    return chunks


# Index the chunks to Qdrant collection
def index_to_qdrant(
    chunks: list[MediChunk],
    url: str = QDRANT_URL,
    collection: str = QDRANT_COLLECTION,
) -> int:
    if not chunks:
        return 0

    # 1. Encode dense vectors (semantic)
    dense_model = SentenceTransformer(EMBEDDING_MODEL)
    dense_vectors = dense_model.encode([c.contextualized_text for c in chunks])

    # 2. Encode sparse vectors (BM25 keywords)
    sparse_model = SparseTextEmbedding(SPARSE_MODEL)
    sparse_vectors = list(sparse_model.embed([c.text for c in chunks]))

    # 3. Create hybrid collection if it doesn't exist
    client = QdrantClient(url=url)
    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config={
                DENSE_VECTOR: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                SPARSE_VECTOR: SparseVectorParams(modifier=Modifier.IDF),
            },
        )

    # 4. Upsert points with both vectors + metadata payload
    points = [
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
            vector={
                DENSE_VECTOR: dense_vector.tolist(),
                SPARSE_VECTOR: SparseVector(
                    indices=sparse_vector.indices.tolist(),
                    values=sparse_vector.values.tolist(),
                ),
            },
            payload=chunk.model_dump(),
        )
        for chunk, dense_vector, sparse_vector in zip(chunks, dense_vectors, sparse_vectors)
    ]
    client.upsert(collection_name=collection, points=points)
    return len(points)


def ingest(root: Path = Path("."), url: str = QDRANT_URL) -> int:
    print("Chunking documents...")
    chunks = convert_all_documents(root)
    print(f"  {len(chunks)} chunks from {len(FILE_PATHS)} files")

    print(f"Indexing to Qdrant collection '{QDRANT_COLLECTION}'...")
    count = index_to_qdrant(chunks, url=url)
    print(f"  {count} points stored (dense + sparse vectors each)")
    return count


if __name__ == "__main__":
    ingest()
