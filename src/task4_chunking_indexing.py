"""
Task 4 — Chunking & Indexing vào Vector Store.

Pipeline:
    1. Đọc toàn bộ markdown files từ data/standardized/
    2. Chunk bằng RecursiveCharacterTextSplitter
    3. Embed bằng model BAAI/bge-m3
    4. Index vào ChromaDB (persistent local)

Lưu ý quan trọng: nếu sau này đổi corpus (đổi chủ đề, thêm/bớt tài liệu), phải XÓA
chroma_db/ cũ trước khi reindex — nếu không, chunk cũ và mới sẽ tồn tại lẫn lộn
trong cùng collection, retrieval sẽ trả về kết quả rác từ dữ liệu cũ.
"""

from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


# =============================================================================
# CONFIGURATION — Lý do lựa chọn
# =============================================================================

# Chunking: RecursiveCharacterTextSplitter
# - Lý do chọn: cắt theo thứ tự ưu tiên [\n\n, \n, ". ", " "] giữ nguyên cấu trúc
#   đoạn văn, không cắt đôi câu, an toàn cho cả tài liệu luật và tin tức.
# - Chunk size 800: đủ để chứa 1-2 đoạn văn, vừa vặn context window embedding,
#   không quá nhỏ để mất ngữ nghĩa, không quá lớn để nhiễu khi retrieve.
# - Overlap 100 (~12.5%): đủ để 1 câu nằm ở cuối chunk A vẫn xuất hiện ở đầu
#   chunk B, tránh cắt đôi thông tin quan trọng.
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"

# Embedding: BAAI/bge-m3
# - Lý do chọn: multilingual mạnh (cả tiếng Việt lẫn tiếng Anh), dim 1024 cho chất
#   lượng biểu diễn cao hơn MiniLM (384). Phù hợp domain chính sách/tin tức tiếng Việt.
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# Vector store: ChromaDB
# - Lý do chọn: persistent local (không cần Docker/server), cosine similarity built-in,
#   metadata filter sẵn, đơn giản cho starter.
VECTOR_STORE = "chromadb"
COLLECTION_NAME = "university_services_docs"


# =============================================================================
# IMPLEMENTATION
# =============================================================================

# Cache embedding model để tránh reload nhiều lần (model nặng ~2GB)
_EMBEDDING_MODEL_INSTANCE = None


def get_embedding_model():
    """
    Lazy-load embedding model. Trả về instance SentenceTransformer.

    Được Task 5 dùng lại để đảm bảo query và document dùng chung model.
    """
    global _EMBEDDING_MODEL_INSTANCE
    if _EMBEDDING_MODEL_INSTANCE is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDING_MODEL_INSTANCE = SentenceTransformer(EMBEDDING_MODEL)
    return _EMBEDDING_MODEL_INSTANCE


def get_chroma_client():
    """Trả về ChromaDB PersistentClient (idempotent)."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    """
    Trả về collection dùng chung cho cả Task 4 (index) và Task 5 (search).
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of {'content': str, 'metadata': {'source': str, 'type': str}}
    """
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8").strip()
        except Exception:
            continue
        if not content:
            continue

        # Phân loại theo thư mục: legal/ hay news/
        rel_path = md_file.relative_to(STANDARDIZED_DIR).as_posix()
        doc_type = "legal" if rel_path.startswith("legal") else "news"

        documents.append({
            "content": content,
            "metadata": {
                "source": md_file.name,
                "type": doc_type,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents theo RecursiveCharacterTextSplitter.

    Returns:
        List of {'content': str, 'metadata': dict} — mỗi item là 1 chunk
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, chunk_text in enumerate(splits):
            chunks.append({
                "content": chunk_text,
                "metadata": {**doc["metadata"], "chunk_index": i},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng BAAI/bge-m3.

    Returns:
        Mỗi chunk dict được thêm key 'embedding': list[float]
    """
    if not chunks:
        return chunks

    model = get_embedding_model()
    texts = [c["content"] for c in chunks]

    # batch_size để tránh OOM khi corpus lớn
    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb.tolist()
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào ChromaDB. Dùng upsert theo id để idempotent.
    """
    if not chunks:
        return

    collection = get_collection()

    ids = [
        f"{c['metadata']['source']}_chunk_{c['metadata']['chunk_index']}"
        for c in chunks
    ]
    collection.upsert(
        ids=ids,
        documents=[c["content"] for c in chunks],
        embeddings=[c["embedding"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    if not docs:
        print("⚠ Không có document nào trong data/standardized/. Dừng pipeline.")
        print("  Hãy chạy Task 1 → Task 3 trước, hoặc copy file .md vào đó.")
        return

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()