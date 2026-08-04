"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

from pathlib import Path
from typing import Optional

# Config - phải khớp với Task 4
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "university_services_docs"  # Default từ Task 4

# Singleton cho model
_embedding_model = None


def get_embedding_model():
    """Load và cache embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def get_collection():
    """Get hoặc create ChromaDB collection."""
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    model = get_embedding_model()
    query_vector = model.encode(query).tolist()

    collection = get_collection()
    
    try:
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
    except Exception:
        return []

    if not results or not results.get("documents") or not results["documents"][0]:
        return []

    output = []
    for doc, meta, dist in zip(
        results["documents"][0], 
        results["metadatas"][0] if results["metadatas"] else [],
        results["distances"][0] if results["distances"] else []
    ):
        # ChromaDB distance -> cosine similarity
        score = max(0.0, 1.0 - dist)
        output.append({
            "content": doc, 
            "score": round(score, 4), 
            "metadata": meta or {}
        })

    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


def hyde_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Hypothetical Document Embeddings (HyDE) search.
    
    Tạo hypothetical document từ query, rồi embed document đó
    thay vì embed query trực tiếp.
    """
    import os
    
    hyde_prompt = f"""Generate a hypothetical document that answers the following question.
Only output the document content, no explanations.

Question: {query}

Hypothetical Document:"""
    
    # Use local model hoặc OpenAI nếu có key
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    
    if api_key:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") if os.getenv("OPENROUTER_API_KEY") else None
        
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": hyde_prompt}],
            max_tokens=200,
        )
        hypothetical_doc = response.choices[0].message.content
    else:
        # Fallback: use query as hypothetical doc
        hypothetical_doc = query
    
    # Embed hypothetical document
    return semantic_search(hypothetical_doc, top_k=top_k)


if __name__ == "__main__":
    # Test
    results = semantic_search("what is the tuition fee", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
