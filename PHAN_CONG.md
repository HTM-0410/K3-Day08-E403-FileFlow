# Phân Công Công Việc - RAG Pipeline Luật Lao Động

**Chủ đề:** Trợ Lý Hỏi Đáp Luật Lao Động Cho Người Trẻ  
**Nhóm:** 3 thành viên  
**Thời lượng:** 3 giờ (180 phút)  
**Tổng điểm:** 100 điểm

---

## Tổng Quan Phân Công

| Thành viên | Vai trò | Nhiệm vụ chính |
|------------|---------|----------------|
| **Role 1** | Team Leader & Data Specialist | CP0 + Task 1-4: Thu thập & xử lý dữ liệu |
| **Role 2** | Retrieval & Generation Specialist | Task 5-10: Search modules + Pipeline + Generation |
| **Role 3** | Evaluation & QA Engineer | Test + Evaluation + Chatbot UI |

---

## Role 1 — Team Leader & Data Specialist

### CP0: Setup Môi Trường (0:00 - 0:10)

| STT | Công việc | Output |
|-----|-----------|--------|
| 1 | Tạo `.venv` và activate | Virtual environment sẵn sàng |
| 2 | Cài `requirements.txt` | Dependencies installed |
| 3 | Cài `markitdown[pdf]` | Document converter hoạt động |
| 4 | Cài `playwright install chromium` | Browser ready cho crawl |
| 5 | Tạo `.env` với `OPENROUTER_API_KEY` | API key configured |

### Task 1: Thu Thập Văn Bản Pháp Luật (0:10 - 0:20)

**Yêu cầu:** ≥3 file PDF/DOCX trong `data/landing/legal/`

| STT | Văn bản | File |
|-----|---------|------|
| 1 | Bộ luật Lao động 2019 (Luật 45/2019/QH14) | `bo-luat-lao-dong-2019.pdf` |
| 2 | Nghị định 145/2020/NĐ-CP | `nghi-dinh-145-2020-nd-cp.pdf` |
| 3 | Thông tư 10/2020/TT-BLĐTBXH | `thong-tu-10-2020-tt-bldtbxh.pdf` |

**Nguồn gợi ý:**
- https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=139264 (Bộ luật Lao động)
- https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=146059 (Nghị định 145)

### Task 2: Crawl Bài Viết Tin Tức (0:20 - 0:35)

**Yêu cầu:** ≥5 file trong `data/landing/news/`

| STT | Chủ đề | File |
|-----|--------|------|
| 1 | Thử việc | `article_01.json` |
| 2 | Chấm dứt HĐLĐ | `article_02.json` |
| 3 | Tiền lương | `article_03.json` |
| 4 | Bảo hiểm xã hội | `article_04.json` |
| 5 | Nghỉ phép | `article_05.json` |

**Nguồn gợi ý:**
- https://luatvietnam.vn/labor/thoi-viec-hop-dong-ld-46-2019-qh14.html
- https://luatvietnam.vn/labor/ket-thuc-hop-dong-lao-dong-46-2019-qh14.html
- https://luatvietnam.vn/labor/tien-luong-46-2019-qh14.html

### Task 3: Convert Sang Markdown (0:35 - 0:40)

**Yêu cầu:** Files `.md` trong `data/standardized/`

```bash
python -m src.task3_convert_markdown
```

**Output structure:**
```
data/standardized/
├── legal/
│   ├── bo-luat-lao-dong-2019.md
│   ├── nghi-dinh-145-2020-nd-cp.md
│   └── thong-tu-10-2020-tt-bldtbxh.md
└── news/
    ├── article_01.md
    └── ...
```

### Task 4: Chunking & Indexing (0:40 - 1:00)

**Yêu cầu:** ChromaDB index trong `chroma_db/`

| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| CHUNK_SIZE | 800 | Đủ dài để giữ context, đủ ngắn để retrieval chính xác |
| CHUNK_OVERLAP | 100 | Tránh mất thông tin ở boundary |
| EMBEDDING_MODEL | BAAI/bge-m3 | Multilingual, tốt cho tiếng Việt |
| EMBEDDING_DIM | 1024 | Standard cho bge-m3 |

```bash
python -m src.task4_chunking_indexing
```

---

## Role 2 — Retrieval & Generation Specialist

### Task 5: Semantic Search (0:35 - 0:45)

**File:** `src/task5_semantic_search.py`

```python
def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
    """
    ...
```

**Công nghệ:** Cosine similarity với ChromaDB

### Task 6: Lexical Search (0:45 - 1:00)

**File:** `src/task6_lexical_search.py`

```python
def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
    """
    ...
```

**Công nghệ:** BM25 (từ `rank_bm25`)

### Task 7: RRF Reranking (1:00 - 1:10)

**File:** `src/task7_reranking.py`

```python
def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """
    Re-score và re-order candidates dùng RRF formula.
    RRF(d) = Σ 1/(60 + r(d))
    """
    ...
```

### Task 8: PageIndex Vectorless Fallback (1:10 - 1:20)

**File:** `src/task8_pageindex_vectorless.py`

```python
def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval dùng PageIndex SDK.
    Fallback khi hybrid search không đủ tốt.
    """
    ...
```

### Task 9: Hybrid Retrieval Pipeline (1:20 - 1:35)

**File:** `src/task9_retrieval_pipeline.py`

```python
def retrieve(query: str, top_k: int = 5, score_threshold: float = 0.48) -> list[dict]:
    """
    1. Semantic search + Lexical search
    2. RRF fusion
    3. Fallback sang PageIndex nếu cosine < 0.48
    """
    ...
```

**⚠️ Lưu ý quan trọng:**
- So sánh `score_threshold` với **Cosine similarity gốc** (thang [0,1])
- KHÔNG so với điểm RRF (luôn ~0.016, không có ý nghĩa)

### Task 10: Generation Có Citation (1:35 - 1:45)

**File:** `src/task10_generation.py`

```python
def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Pattern: quan trọng nhất ở đầu và cuối, ít quan trọng ở giữa.
    Ví dụ: [1, 3, 5, 4, 2] thay vì [1, 2, 3, 4, 5]
    """
    n = len(chunks)
    front = chunks[:n//2]
    back = chunks[n//2:][::-1]
    return front + back

def generate_with_citation(query: str, context_chunks: list[dict]) -> dict:
    """
    Trả về {'answer': str, 'sources': list}
    Citation format: [Nguồn: Bộ luật Lao động 2019, Điều 16]
    """
    ...
```

---

## Role 3 — Evaluation & QA Engineer

### Test & Verify (1:45)

```bash
pytest tests/test_individual.py -v
```

**Mục tiêu:** ≥35/35 tests passed

### Golden Dataset (1:45 - 2:00)

**File:** `group_project/evaluation/golden_dataset.json`

**Yêu cầu:** ≥15 cặp Q&A

| # | Câu hỏi |
|---|----------|
| 1 | Thời gian thử việc tối đa là bao lâu theo luật? |
| 2 | Lương thử việc tối thiểu bằng bao nhiêu % lương chính thức? |
| 3 | Công ty có được sa thải nhân viên qua tin nhắn Zalo không? |
| 4 | Thời hạn báo trước khi chấm dứt HĐLĐ là bao lâu? |
| 5 | Hồ sơ ký kết hợp đồng lao động gồm những gì? |
| 6 | Quy định về thời giờ làm việc bình thường là mấy giờ? |
| 7 | Lao động nữ được nghỉ thai sản bao lâu? |
| 8 | Tiền lương làm thêm giờ được tính như thế nào? |
| 9 | Khi nào người sử dụng lao động được phép kết thúc HĐLĐ? |
| 10 | Học sinh, sinh viên có được ký hợp đồng học việc không? |
| 11 | Điều kiện để HĐLĐ xác định thời hạn trở thành HĐLĐ không xác định thời hạn? |
| 12 | Người lao động có được từ chối làm việc ban đêm không? |
| 13 | Quyền đơn phương chấm dứt HĐLĐ của người lao động? |
| 14 | Công ty có phải đóng bảo hiểm xã hội cho lao động không? |
| 15 | Lương khoán được tính như thế nào theo luật? |

### Evaluation Pipeline (2:00 - 2:10)

**File:** `group_project/evaluation/eval_pipeline.py`

**Framework:** RAGAS

**Metrics cần đo:**
| Metric | Mô tả | Threshold |
|--------|--------|------------|
| Faithfulness | Câu trả lời bám đúng context | ≥0.7 |
| Answer Relevance | Câu trả lời đúng câu hỏi | ≥0.7 |
| Context Recall | Retriever lấy đủ evidence | ≥0.7 |
| Context Precision | % context thực sự hữu ích | ≥0.7 |

### A/B Comparison (2:10 - 2:15)

**File:** `group_project/evaluation/results.md`

So sánh ít nhất 2 configs:
- Config A: Hybrid search (Semantic + BM25)
- Config B: Dense-only (Semantic only)

### Chatbot UI (1:45 - 2:15)

**File:** `app.py`

**Tính năng:**
- Giao diện chat (Streamlit)
- Trả lời có citation
- Hiển thị source documents
- Hỗ trợ follow-up questions

---

## Timeline Checkpoint Tổng Hợp

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 0:00-0:10  │ CP0: Setup môi trường, .env với OPENROUTER_API_KEY          │
├────────────┼───────────────────────────────────────────────────────────────┤
│            │ CP1: Thu thập & Xử lý Dữ liệu (Role 1)                       │
│ 0:10-0:35  │ ├── Task 1: ≥3 PDF trong data/landing/legal/                 │
│            │ ├── Task 2: ≥5 news trong data/landing/news/                  │
│            │ └── Task 3: Convert sang Markdown                              │
├────────────┼───────────────────────────────────────────────────────────────┤
│            │ CP2: Search Modules (Role 2)                                  │
│ 0:35-1:00  │ ├── Task 4: Chunking + ChromaDB indexing (Role 1)             │
│            │ ├── Task 5: Semantic search                                   │
│            │ └── Task 6: Lexical BM25 search                               │
├────────────┼───────────────────────────────────────────────────────────────┤
│            │ CP3: Advanced Retrieval (Role 2)                              │
│ 1:00-1:20  │ ├── Task 7: RRF Reranking                                    │
│            │ └── Task 8: PageIndex Vectorless Fallback                      │
├────────────┼───────────────────────────────────────────────────────────────┤
│            │ CP4: Pipeline Hoàn Chỉnh ⭐ MỐC 50Đ                           │
│ 1:20-1:45  │ ├── Task 9: Hybrid Retrieval Pipeline                         │
│            │ └── Task 10: Generation + Citation                            │
├────────────┼───────────────────────────────────────────────────────────────┤
│            │ CP5: Bài Nhóm                                                 │
│ 1:45-2:15  │ ├── Golden Dataset ≥15 Q&A                                   │
│            │ ├── RAGAS Evaluation                                          │
│            │ ├── A/B Comparison                                             │
│            │ └── Chatbot UI                                                 │
├────────────┼───────────────────────────────────────────────────────────────┤
│ 2:15-3:00  │ CP6: Demo Live + Nộp bài                                    │
└────────────┴───────────────────────────────────────────────────────────────┘
```

---

## Cách Chấm Điểm

### Điểm Cá Nhân — 50 điểm

| Task | Nội dung | Điểm |
|------|----------|-------|
| 1 | Thu thập văn bản pháp luật (≥3 files) | 3 |
| 2 | Crawl bài viết (≥5 files) | 3 |
| 3 | Convert Markdown | 4 |
| 4 | Chunking + ChromaDB | 7 |
| 5 | Semantic search | 6 |
| 6 | Lexical search (BM25) | 6 |
| 7 | RRF Reranking | 6 |
| 8 | PageIndex | 4 |
| 9 | Pipeline + Fallback | 7 |
| 10 | Generation + Citation | 4 |
| **Tổng** | | **50** |

### Điểm Nhóm — 30 điểm

| Tiêu chí | Điểm |
|----------|------|
| RAG Chatbot demo hoạt động | 8 |
| Tích hợp pipeline Task 1-10 | 4 |
| Kiến trúc rõ ràng + README | 3 |
| Chất lượng câu trả lời (citation) | 3 |
| Golden dataset ≥15 Q&A | 3 |
| Eval với ≥4 metrics | 4 |
| A/B comparison ≥2 configs | 3 |
| Báo cáo + phân tích | 2 |

### Bonus — 20 điểm

| Tiêu chí | Điểm |
|----------|------|
| Giải thích cơ chế lexical search khác BM25 | 5 |
| Implement HyDE / Query Expansion | 5 |
| Deploy chatbot online | 4 |
| Conversation memory (multi-turn) | 3 |
| UI/UX chất lượng cao | 3 |

---

## Các Lỗi Thường Gặp

| # | Lỗi | Nguyên nhân | Cách sửa |
|---|-----|-------------|----------|
| 1 | `MissingDependencyException` ở Task 3 | Thiếu markitdown pdf | `pip install "markitdown[pdf]"` |
| 2 | `BrowserType.launch` ở Task 2 | Chưa cài Chromium | `playwright install chromium` |
| 3 | `UnicodeEncodeError` trên Windows | Mã hóa console | `$env:PYTHONIOENCODING="utf-8"` |
| 4 | Fallback không bao giờ chạy | So với điểm RRF thay vì Cosine | Sửa: `dense_results[0]["score"] < 0.48` |
| 5 | Dữ liệu cũ lẫn mới | Chưa xóa `chroma_db/` | `Remove-Item -Recurse -Force chroma_db` |
| 6 | Rate Limit 429 ở RAGAS | Gọi LLM quá nhiều | Giảm số câu hỏi trong golden_dataset |

---

## Hướng Dẫn Chạy Nhanh

```bash
# Setup môi trường
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Copy và cấu hình .env
copy .env.example .env
# Điền OPENROUTER_API_KEY vào .env

# Chạy từng Task (Role 1)
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
python -m src.task3_convert_markdown
python -m src.task4_chunking_indexing

# Role 2
python -m src.task5_semantic_search
python -m src.task6_lexical_search
# ...

# Kiểm tra điểm
pytest tests/test_individual.py -v

# Chạy Chatbot
streamlit run app.py
```

---

*File tạo: 2026-08-04*  
*Chủ đề: Trợ Lý Hỏi Đáp Luật Lao Động Cho Người Trẻ*
