"""
Task 1 & 2: Crawl dữ liệu luật lao động Việt Nam - v3
"""

import json
import re
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data"
LANDING_LEGAL = DATA_DIR / "landing" / "legal"
LANDING_NEWS = DATA_DIR / "landing" / "news"

LANDING_LEGAL.mkdir(parents=True, exist_ok=True)
LANDING_NEWS.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_content(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
        tag.decompose()
    
    selectors = ['article', 'main', '.content', '#content', '.post-content', 
                 '.article-content', '.entry-content', '.article-body', '.detail-content',
                 '.field-item', '.node-content', '.article', '.docnoi']
    
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            return clean_text(elem.get_text(separator='\n'))
    
    body = soup.find('body')
    if body:
        return clean_text(body.get_text(separator='\n'))
    return ""


def crawl_url(url: str) -> dict:
    try:
        print(f"  Crawling: {url[:80]}...")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_elem = soup.find('h1') or soup.select_one('.page-title') or soup.select_one('title')
        title = clean_text(title_elem.get_text()) if title_elem else "Untitled"
        
        content = extract_content(soup)
        
        desc = ""
        desc_elem = soup.select_one('meta[name="description"]')
        if desc_elem:
            desc = desc_elem.get('content', '')
        
        return {
            "url": url,
            "title": title,
            "description": desc,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content,
            "source": url.split('/')[2] if '/' in url else "unknown",
            "status_code": response.status_code,
            "content_length": len(content),
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def save_json(data: dict, filepath: Path):
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✓ Saved: {filepath.name} ({data.get('content_length', 0)} chars)")


def collect_legal_documents():
    """Task 1: Thu thập văn bản pháp luật VN (≥3 files)"""
    print("\n" + "="*50)
    print("TASK 1: Thu thập văn bản pháp luật VN")
    print("="*50)
    
    legal_sources = [
        {
            "url": "https://english.luatvietnam.vn/labor-code-no-45-2019-qh14-dated-november-20-2019-of-the-national-assembly-179015-doc1.html",
            "filename": "bo-luat-lao-dong-2019-en.json",
            "title": "Labor Code 2019 (English)"
        },
        {
            "url": "https://luatvietnam.vn/lao-dong/bo-luat-lao-dong-2019-so-45-2019-qh14-179015-d1.html",
            "filename": "bo-luat-lao-dong-2019-vn.json",
            "title": "Bộ luật Lao động 2019 (Tiếng Việt)"
        },
        {
            "url": "https://english.luatvietnam.vn/decree-no-145-2020-nd-cp-dated-on-december-14-2020-of-the-government-detailing-and-guiding-the-implementation-of-a-number-of-articles-of-the-labor-c-195612-doc1.html",
            "filename": "nghi-dinh-145-2020-en.json",
            "title": "Nghị định 145/2020/NĐ-CP (English)"
        },
        {
            "url": "https://thuvienphapluat.vn/van-ban/Lao-dong-Tien-luong/Nghi-dinh-145-2020-ND-CP-huong-dan-Bo-luat-Lao-dong-ve-dieu-kien-lao-dong-quan-he-lao-dong-459400.aspx",
            "filename": "nghi-dinh-145-2020-vn.json",
            "title": "Nghị định 145/2020/NĐ-CP (Tiếng Việt)"
        },
    ]
    
    count = 0
    for item in legal_sources:
        print(f"\n[{count+1}/{len(legal_sources)}] {item['title']}")
        data = crawl_url(item['url'])
        if data and data.get('content_markdown') and len(data.get('content_markdown', '')) > 200:
            save_json(data, LANDING_LEGAL / item['filename'])
            count += 1
        else:
            print(f"  ⚠ No content extracted")
    
    print(f"\n✓ Task 1: {count} văn bản")
    return count


def collect_news_articles():
    """Task 2: Crawl bài viết (≥5 files)"""
    print("\n" + "="*50)
    print("TASK 2: Crawl bài viết luật lao động VN")
    print("="*50)
    
    news_urls = [
        {
            "url": "https://luatvietnam.vn/lao-dong/tien-luong-theo-luat-lao-dong-2019-179015-d1.html",
            "filename": "article_01.json",
            "title": "Tiền lương"
        },
        {
            "url": "https://luatvietnam.vn/lao-dong/bao-hiem-xa-hoi-theo-luat-lao-dong-2019-179015-d1.html",
            "filename": "article_02.json",
            "title": "Bảo hiểm xã hội"
        },
        {
            "url": "https://luatvietnam.vn/lao-dong/nghi-phep-theo-luat-lao-dong-2019-179015-d1.html",
            "filename": "article_03.json",
            "title": "Nghỉ phép"
        },
        {
            "url": "https://luatvietnam.vn/lao-dong/thoi-gio-lam-viec-theo-luat-lao-dong-2019-179015-d1.html",
            "filename": "article_04.json",
            "title": "Thời giờ làm việc"
        },
        {
            "url": "https://luatvietnam.vn/lao-dong/lam-them-gio-theo-luat-lao-dong-2019-179015-d1.html",
            "filename": "article_05.json",
            "title": "Làm thêm giờ"
        },
    ]
    
    count = 0
    for item in news_urls:
        print(f"\n[{count+1}/{len(news_urls)}] {item['title']}")
        data = crawl_url(item['url'])
        if data and data.get('content_markdown') and len(data.get('content_markdown', '')) > 200:
            save_json(data, LANDING_NEWS / item['filename'])
            count += 1
        else:
            print(f"  ⚠ No content extracted")
    
    print(f"\n✓ Task 2: {count} bài viết")
    return count


def main():
    print("="*60)
    print("FILEFLOW - THU THẬP DỮ LIỆU LUẬT LAO ĐỘNG VN")
    print("="*60)
    
    legal_count = collect_legal_documents()
    news_count = collect_news_articles()
    
    print("\n" + "="*60)
    print("TỔNG KẾT")
    print("="*60)
    print(f"  legal/: {legal_count} files")
    print(f"  news/: {news_count} files")
    print(f"  Tổng: {legal_count + news_count} files")
    
    if legal_count >= 3 and news_count >= 5:
        print("\n✓ CP1 PASS: Đủ dữ liệu")
    else:
        print(f"\n⚠ Cần thêm: {max(0, 3-legal_count)} legal, {max(0, 5-news_count)} news")


if __name__ == "__main__":
    main()
