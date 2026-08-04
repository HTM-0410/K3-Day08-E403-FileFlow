"""
Task 6 — Lexical Search Module (BM25).

Thuật toán BM25 (Best Matching 25):
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1))
                                  / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)

Cơ chế BM25 phù hợp với truy vấn có từ khoá chính xác (số hiệu văn bản,
tên riêng, mã quyết định) — đây là điểm yếu của semantic search.

Lazy-load corpus từ ChromaDB collection (chính là những chunk đã index ở Task 4)
để đảm bảo dense và sparse search làm việc trên cùng một tập tài liệu.
"""

import threading

# Lazy-loaded corpus và BM25 index
_CORPUS: list[dict] = []
_BM25_INSTANCE = None
_CORPUS_LOADED = False
_LOCK = threading.Lock()


def _tokenize(text: str) -> list[str]:
    """
    Tokenize đơn giản cho BM25.
    - Lowercase toàn bộ
    - Tách theo whitespace, bỏ token quá ngắn
    - Với tiếng Việt có thể thay bằng underthesea.word_tokenize để chất lượng cao hơn
      (khuyến nghị cho bonus).
    """
    if not text:
        return []
    tokens = [t for t in text.lower().split() if len(t) > 1]
    return tokens


def _load_corpus_from_chroma():
    """
    Load toàn bộ chunks từ ChromaDB (đã index ở Task 4).
    Điều này đảm bảo BM25 search cùng corpus với semantic search.
    """
    global _CORPUS, _CORPUS_LOADED, _BM25_INSTANCE

    try:
        from .task4_chunking_indexing import get_collection
    except Exception:
        from task4_chunking_indexing import get_collection

    try:
        collection = get_collection()
    except Exception:
        # ChromaDB chưa được cài hoặc chưa init → corpus rỗng
        _CORPUS = []
        _CORPUS_LOADED = True
        _BM25_INSTANCE = None
        return

    if collection.count() == 0:
        _CORPUS = []
        _CORPUS_LOADED = True
        _BM25_INSTANCE = None
        return

    # ChromaDB .get() trả về tất cả document; nếu corpus rất lớn (>10k) nên
    # paginate, nhưng với bài lab này dữ liệu nhỏ nên lấy hết 1 lần được.
    raw = collection.get(include=["documents", "metadatas"])

    _CORPUS = []
    for doc, meta in zip(raw.get("documents", []), raw.get("metadatas", [])):
        _CORPUS.append({
            "content": doc,
            "metadata": meta or {},
        })

    # Build BM25 ngay khi load corpus
    if _CORPUS:
        from rank_bm25 import BM25Okapi
        tokenized_corpus = [_tokenize(doc["content"]) for doc in _CORPUS]
        _BM25_INSTANCE = BM25Okapi(tokenized_corpus)
    else:
        _BM25_INSTANCE = None

    _CORPUS_LOADED = True


def _ensure_loaded():
    """Thread-safe lazy load."""
    with _LOCK:
        if not _CORPUS_LOADED:
            _load_corpus_from_chroma()


def reload_corpus():
    """
    Public API để force reload corpus từ ChromaDB (gọi sau khi reindex ở Task 4
    nếu muốn đảm bảo BM25 luôn mới).
    """
    global _CORPUS_LOADED, _BM25_INSTANCE, _CORPUS
    with _LOCK:
        _CORPUS_LOADED = False
        _BM25_INSTANCE = None
        _CORPUS = []
        _load_corpus_from_chroma()


def get_corpus_size() -> int:
    """Trả về kích thước corpus đã load (cho debug/test)."""
    _ensure_loaded()
    return len(_CORPUS)


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus. Có thể dùng độc lập, không qua ChromaDB.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    from rank_bm25 import BM25Okapi

    tokenized_corpus = [_tokenize(doc["content"]) for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25, corpus


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khoá sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score (có thể > 0, không bounded)
            'metadata': dict
        }
        Sorted by score descending.
    """
    _ensure_loaded()

    if not query or not query.strip():
        return []
    if _BM25_INSTANCE is None or not _CORPUS:
        return []

    tokenized_query = _tokenize(query)
    if not tokenized_query:
        return []

    scores = _BM25_INSTANCE.get_scores(tokenized_query)

    # Lấy top_k theo score
    import numpy as np
    top_indices = np.argsort(scores)[::-1]

    results = []
    for idx in top_indices:
        score = float(scores[idx])
        if score <= 0:
            continue  # bỏ qua doc không match
        results.append({
            "content": _CORPUS[idx]["content"],
            "score": round(score, 4),
            "metadata": _CORPUS[idx]["metadata"],
        })
        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    reload_corpus()
    results = lexical_search("tuition fee payment methods", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")