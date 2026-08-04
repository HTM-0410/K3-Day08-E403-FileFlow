"""
Task 5 — Semantic Search Module (Dense Retrieval).

Tìm kiếm ngữ nghĩa trên ChromaDB dùng Cosine Similarity.
Dùng chung embedding model với Task 4 (`get_embedding_model`).
"""

from .task4_chunking_indexing import get_collection, get_embedding_model


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng Cosine Similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score [0, 1]
            'metadata': dict     # source, type, chunk_index
        }
        Sorted by score descending.
    """
    if not query or not query.strip():
        return []

    # Bước 1: Embed query bằng cùng model ở Task 4
    model = get_embedding_model()
    query_vector = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    # Bước 2: Query vector store (cosine similarity)
    collection = get_collection()

    # Nếu collection rỗng (chưa index) → trả về list rỗng, không crash
    if collection.count() == 0:
        return []

    n_results = min(top_k, collection.count())

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # Bước 3: Convert distance → similarity
    # ChromaDB với cosine space trả distance ∈ [0, 2]; similarity = 1 - distance
    output = []
    docs_list = results.get("documents", [[]])[0]
    metas_list = results.get("metadatas", [[]])[0]
    dists_list = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs_list, metas_list, dists_list):
        score = max(0.0, 1.0 - float(dist))
        output.append({
            "content": doc,
            "score": round(score, 4),
            "metadata": meta or {},
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    results = semantic_search("what is the tuition fee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")