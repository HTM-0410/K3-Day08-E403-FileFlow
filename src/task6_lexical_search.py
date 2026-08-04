"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

from pathlib import Path
import numpy as np

# Config
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Global state
CORPUS: list[dict] = []
_bm25_index = None


def load_corpus() -> list[dict]:
    """Load markdown files từ data/standardized/ vào corpus."""
    global CORPUS
    if CORPUS:
        return CORPUS
    
    corpus = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if len(content) < 50:
                continue
            doc_type = "legal" if "legal" in str(md_file).lower() else "news"
            corpus.append({
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "type": doc_type,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR.parent))
                }
            })
        except Exception:
            continue
    
    CORPUS = corpus
    return CORPUS


def build_bm25_index(corpus: list[dict] = None):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    global _bm25_index
    
    if corpus is None:
        corpus = load_corpus()
    
    from rank_bm25 import BM25Okapi
    
    # Tokenize - simple split
    tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    _bm25_index = BM25Okapi(tokenized_corpus)
    return _bm25_index


def get_bm25_index():
    """Get hoặc build BM25 index."""
    global _bm25_index
    if _bm25_index is None:
        build_bm25_index()
    return _bm25_index


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    if not CORPUS:
        load_corpus()
    
    if not CORPUS:
        return []
    
    bm25 = get_bm25_index()
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Get top_k indices
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "content": CORPUS[idx]["content"],
                "score": float(scores[idx]),
                "metadata": CORPUS[idx]["metadata"]
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    # Test
    results = lexical_search("tuition fee payment methods", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
