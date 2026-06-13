"""Step 3: Rerank hybrid results before passing to the LLM."""

from sentence_transformers import CrossEncoder

from chunker.retriever import hybrid_search

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
RETRIEVE_K = 10  # broad list from hybrid search
RERANK_K = 3    # narrow list for the LLM


def rerank(query: str, chunks: list[dict], top_k: int = RERANK_K) -> list[dict]:
    model = CrossEncoder(RERANKER_MODEL)
    # predict the score for each chunk based on the query and the chunk text
    scores = model.predict([(query, c["text"]) for c in chunks]) # list of scores for each chunk from the cross-encoder model
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True) # sort the chunks by the score in descending order

    results = []
    for chunk, score in ranked[:top_k]:
        result = dict(chunk)
        result["rerank_score"] = float(score)
        results.append(result)
    return results


def retrieve_and_rerank(
    query: str,
    role: str,
    retrieve_k: int = RETRIEVE_K,
    rerank_k: int = RERANK_K,
) -> list[dict]:
    candidates = hybrid_search(query, role, top_k=retrieve_k)
    return rerank(query, candidates, top_k=rerank_k)


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "cashless pre-auth SLA"
    role = sys.argv[2] if len(sys.argv) > 2 else "billing_executive"

    print(f"Retrieving {RETRIEVE_K}, reranking to {RERANK_K}...\n")
    for r in retrieve_and_rerank(query, role):
        print(f"[{r['rerank_score']:.4f}] {r['source_document']}")
        print(f"  {r['text'][:120]}...")
        print()
