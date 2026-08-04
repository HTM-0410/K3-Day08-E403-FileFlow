"""
Task 2 — Crawl >=5 bài viết/thông báo về Luật Lao động (Trợ Lý Hỏi Đáp Luật Lao Động Cho Người Trẻ)

Chủ đề crawl: thử việc, sa thải, làm thêm giờ (OT), nghỉ phép năm — các vấn đề
người lao động trẻ (Gen Z) hay hỏi, lấy từ các trang tin luật uy tín
(thuvienphapluat.vn, luatvietnam.vn, vietnamnet.vn, ...).

Hướng dẫn:
    1. Crawl tối thiểu 5 bài viết (đã liệt kê sẵn trong ARTICLE_URLS).
    2. Dùng Crawl4AI (ưu tiên) — nếu môi trường không cài được Playwright/Chromium,
       tự động fallback sang requests + BeautifulSoup.
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata: url, title, crawl_date, content.

Cài đặt:
    pip install crawl4ai beautifulsoup4 requests --break-system-packages
    playwright install chromium   # bắt buộc cho crawl4ai — pip install crawl4ai KHÔNG tự
                                   # tải browser binary, thiếu bước này sẽ báo lỗi
                                   # "BrowserType.launch: Executable doesn't exist"

Chạy:
    python task2_crawl_news.py
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# Danh sách bài viết luật lao động cần crawl (chủ đề: thử việc, sa thải, OT, nghỉ phép)
ARTICLE_URLS = [
    # Làm thêm giờ (OT) — quy định chi tiết theo Bộ luật Lao động 2019
    "https://thuvienphapluat.vn/phap-luat/ho-tro-phap-luat/quy-dinh-lam-them-gio-2025-moi-nhat-theo-bo-luat-lao-dong-ma-nguoi-lao-dong-va-doanh-nghiep-can-bie-887731-199643.html",

    # Tin tức: xử phạt doanh nghiệp ép làm thêm giờ khi chưa được đồng ý (từ 10/9/2026)
    "https://luatvietnam.vn/tin-van-ban-moi/tu-10-9-2026-cong-ty-ep-nhan-vien-lam-them-gio-khi-chua-dong-y-bi-phat-toi-50-trieu-dong-186-111015-article.html",

    # Thử việc & sa thải — công ty sa thải khi đang thử việc có đúng luật không
    "https://vietnamnet.vn/cong-ty-sa-thai-khi-dang-thu-viec-co-dung-luat-560146.html",

    # Nghỉ phép năm — tổng hợp quy định nghỉ phép năm 2026
    "https://thuvienphapluat.vn/phap-luat/ho-tro-phap-luat/tong-hop-quy-dinh-nghi-phep-nam-2026-danh-cho-nguoi-lao-dong-quy-dinh-nghi-phep-nam-moi-nhat-ra-sao-362735-253204.html",

    # Lương làm thêm giờ & thuế TNCN — điều kiện miễn thuế lương OT từ 01/01/2026
    "https://thuvienphapluat.vn/phap-luat-doanh-nghiep/bai-viet/dieu-kien-de-toan-bo-tien-luong-lam-them-gio-duoc-mien-thue-tncn-tu-01-01-2026-18082.html",

    # Hợp đồng thử việc — bẫy pháp lý khi ký hợp đồng thử việc (bài phân tích thêm, dự phòng)
    "https://luatbacduong.com/bay-phap-ly-khi-ky-hop-dong-thu-viec-quyen-loi-bi-bo-quen-va-rui-ro-cho-doanh-nghiep/",
]


def _clean_text(text: str) -> str:
    """Gọn khoảng trắng thừa, giữ lại xuống dòng giữa các đoạn."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


async def _crawl_with_crawl4ai(url: str) -> dict | None:
    """Crawl bằng Crawl4AI (render JS qua Chromium headless). Trả về None nếu lỗi."""
    try:
        from crawl4ai import AsyncWebCrawler
    except ImportError:
        return None

    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=True)
            if not result or not result.success:
                return None

            title = None
            if getattr(result, "metadata", None):
                title = result.metadata.get("title")
            if not title:
                title = url

            content = (result.markdown or result.cleaned_html or "").strip()
            if not content:
                return None

            return {
                "url": url,
                "title": title.strip(),
                "crawl_date": datetime.now().isoformat(),
                "content": _clean_text(content),
            }
    except Exception as e:
        print(f"  ⚠ Crawl4AI lỗi ({e}), thử fallback requests + BeautifulSoup...")
        return None


def _crawl_with_requests(url: str) -> dict | None:
    """Fallback: requests + BeautifulSoup (không render JS)."""
    import requests
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    # Xoá các thẻ rác trước khi lấy nội dung
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # Ưu tiên tìm khối nội dung chính theo các class/id phổ biến của các trang tin luật VN
    content_selectors = [
        {"class_": "content-detail"},
        {"class_": "article-content"},
        {"class_": "detail-content"},
        {"id": "divContentDocVn"},
        {"class_": "fck_detail"},
    ]
    body = None
    for sel in content_selectors:
        body = soup.find(["div", "article"], **sel)
        if body:
            break
    if not body:
        body = soup.find("article") or soup

    content = body.get_text(separator="\n", strip=True)

    if not content:
        return None

    return {
        "url": url,
        "title": title,
        "crawl_date": datetime.now().isoformat(),
        "content": _clean_text(content),
    }


async def crawl_article(url: str) -> dict:
    """
    Crawl một bài viết và trả về dict chứa metadata + content.
    Thử Crawl4AI trước, nếu không có/thất bại thì fallback requests + BeautifulSoup.

    Returns:
        {
            "url": str,
            "title": str,
            "crawl_date": str (ISO format),
            "content": str
        }
    """
    result = await _crawl_with_crawl4ai(url)
    if result:
        return result

    # Fallback chạy sync trong thread riêng để không block event loop
    result = await asyncio.to_thread(_crawl_with_requests, url)
    if result:
        return result

    raise RuntimeError(f"Không thể crawl được nội dung từ {url}")


async def crawl_all():
    """Crawl toàn bộ bài viết trong ARTICLE_URLS."""
    setup_directory()

    ok, failed = 0, []
    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        try:
            article = await crawl_article(url)
        except Exception as e:
            print(f"  ✗ Lỗi: {e}")
            failed.append(url)
            continue

        # Lưu file JSON
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Saved: {filepath} ({len(article['content'])} ký tự)")
        ok += 1

    print(f"\nHoàn tất: {ok}/{len(ARTICLE_URLS)} bài crawl thành công.")
    if failed:
        print("Các URL lỗi:")
        for u in failed:
            print(f"  - {u}")


if __name__ == "__main__":
    if not ARTICLE_URLS:
        print("⚠ Hãy điền ARTICLE_URLS trước khi chạy!")
    else:
        asyncio.run(crawl_all())