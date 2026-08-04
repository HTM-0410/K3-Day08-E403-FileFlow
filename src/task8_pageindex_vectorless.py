"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API

Lưu ý: API `/retrieval` của PageIndex hiện đã deprecated (vẫn hoạt động, nhưng response
có field "deprecation" cảnh báo) và trả kết quả trong "retrieved_nodes" — mỗi node có
"relevant_contents": list[list[{section_title, relevant_content}]]. In response thật ra
(json.dumps(...)) trước khi viết logic parse, đừng đoán schema từ ví dụ code cũ.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Upload toàn bộ markdown documents lên PageIndex.
    """
    if not PAGEINDEX_API_KEY:
        print("⚠ PAGEINDEX_API_KEY not set")
        return []
    
    try:
        from pageindex.client import PageIndexClient
    except ImportError:
        print("⚠ pageindex package not installed")
        return []
    
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    uploaded_ids = []
    
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        try:
            # Convert markdown to PDF first
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            content = md_file.read_text(encoding="utf-8")
            pdf.set_font("Helvetica", size=10)
            
            for line in content.split('\n'):
                if line.startswith('# '):
                    pdf.set_font("Helvetica", size=14)
                    pdf.multi_cell(0, 8, line[2:])
                    pdf.set_font("Helvetica", size=10)
                elif line.startswith('## '):
                    pdf.set_font("Helvetica", size=12)
                    pdf.multi_cell(0, 7, line[3:])
                    pdf.set_font("Helvetica", size=10)
                elif line.startswith('### '):
                    pdf.set_font("Helvetica", size=11)
                    pdf.multi_cell(0, 6, line[4:])
                    pdf.set_font("Helvetica", size=10)
                else:
                    pdf.multi_cell(0, 5, line)
            
            temp_pdf = md_file.with_suffix('.pdf')
            pdf.output(str(temp_pdf))
            
            # Upload to PageIndex
            resp = client.submit_document(str(temp_pdf))
            doc_id = resp.get("doc_id") or resp.get("id")
            uploaded_ids.append({"file": md_file.name, "doc_id": doc_id})
            print(f"  ✓ Uploaded: {md_file.name} -> {doc_id}")
            
            # Clean up temp PDF
            temp_pdf.unlink()
            
        except Exception as e:
            print(f"  ✗ Failed: {md_file.name}: {e}")
            continue
    
    return uploaded_ids


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    Dùng làm fallback khi hybrid search không có kết quả tốt.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'   # Đánh dấu nguồn retrieval
        }
    """
    if not PAGEINDEX_API_KEY:
        print("⚠ PAGEINDEX_API_KEY not set")
        return []
    
    try:
        from pageindex.client import PageIndexClient
    except ImportError:
        print("⚠ pageindex package not installed")
        return []
    
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    
    # Submit query
    try:
        resp = client.submit_query(query=query)
        retrieval_id = resp.get("retrieval_id") or resp.get("id")
        
        # Poll until completed
        max_retries = 10
        for _ in range(max_retries):
            time.sleep(1)
            retrieval = client.get_retrieval(retrieval_id)
            if retrieval.get("status") == "completed":
                break
            if retrieval.get("status") == "failed":
                print("⚠ PageIndex retrieval failed")
                return []
        
        # Parse response
        results = []
        retrieved_nodes = retrieval.get("retrieved_nodes", [])
        
        for rank, node in enumerate(retrieved_nodes[:top_k], 1):
            relevant_contents = node.get("relevant_contents", [])
            
            for group in relevant_contents:
                if isinstance(group, list):
                    for item in group:
                        if isinstance(item, dict):
                            content = item.get("relevant_content", "")
                            if content:
                                results.append({
                                    "content": content,
                                    "score": float(1.0 - rank * 0.15),
                                    "metadata": {
                                        "section": item.get("section_title", ""),
                                        "source": "pageindex"
                                    },
                                    "source": "pageindex"
                                })
                                if len(results) >= top_k:
                                    break
                elif isinstance(group, dict):
                    content = group.get("relevant_content", "")
                    if content:
                        results.append({
                            "content": content,
                            "score": float(1.0 - rank * 0.15),
                            "metadata": {
                                "section": group.get("section_title", ""),
                                "source": "pageindex"
                            },
                            "source": "pageindex"
                        })
                        if len(results) >= top_k:
                            break
            
            if len(results) >= top_k:
                break
        
        return results[:top_k]
        
    except Exception as e:
        print(f"⚠ PageIndex error: {e}")
        return []


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong file .env")
        print("  Đăng ký tại: https://pageindex.ai/")
    else:
        print("Uploading documents...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("tuition fee payment methods", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
