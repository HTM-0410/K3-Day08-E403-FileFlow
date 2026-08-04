"""
Task 1 & 2 - Crawl dữ liệu pháp luật lao động từ nhiều nguồn.
Sử dụng Wikipedia (EN/VN), và các nguồn mở khác.
"""

import json
import re
import requests
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

# Cấu hình
DATA_DIR = Path(__file__).parent.parent / "data"
LEGAL_DIR = DATA_DIR / "landing" / "legal"
NEWS_DIR = DATA_DIR / "landing" / "news"

LEGAL_DIR.mkdir(parents=True, exist_ok=True)
NEWS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_wiki_content(soup: BeautifulSoup) -> str:
    content = soup.select_one('#mw-content-text') or soup.select_one('.mw-parser-output')
    if content:
        for tag in content.find_all(['script', 'style', 'table', 'sup', 'nav', 'span', 'noscript']):
            tag.decompose()
        return clean_text(content.get_text(separator='\n'))
    return ""


def extract_content(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
        tag.decompose()
    
    selectors = ['article', 'main', '.content', '#content', '.post-content', 
                 '.article-content', '.entry-content', '.article-body']
    
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
        print(f"  Crawling: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_elem = soup.find('h1') or soup.select_one('title')
        title = clean_text(title_elem.get_text()) if title_elem else "Untitled"
        
        if 'wikipedia.org' in url:
            content = extract_wiki_content(soup)
        else:
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
        return {
            "url": url,
            "title": "ERROR",
            "error": str(e),
            "date_crawled": datetime.now().isoformat(),
        }


def save_json(data: dict, filepath: Path):
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✓ Saved: {filepath.name}")


# === TASK 1: Văn bản pháp luật ===
def collect_legal_documents():
    print("\n" + "="*50)
    print("TASK 1: Thu thập văn bản pháp luật")
    print("="*50)
    
    legal_urls = [
        {
            "url": "https://en.wikipedia.org/wiki/Labour_law",
            "filename": "labour-law-overview.json",
            "title": "Labour Law Overview"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Employment_contract",
            "filename": "employment-contract.json",
            "title": "Employment Contract"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Minimum_wage",
            "filename": "minimum-wage.json",
            "title": "Minimum Wage"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Working_time",
            "filename": "working-time.json",
            "title": "Working Time"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Social_security",
            "filename": "social-security.json",
            "title": "Social Security"
        },
    ]
    
    count = 0
    for item in legal_urls:
        print(f"\n[{count+1}/{len(legal_urls)}] {item['title']}")
        data = crawl_url(item['url'])
        if data.get('content_markdown') and len(data.get('content_markdown', '')) > 200:
            filepath = LEGAL_DIR / item['filename']
            save_json(data, filepath)
            count += 1
    
    print(f"\n✓ Task 1: {count} văn bản")
    return count


# === TASK 2: Tin tức/Hướng dẫn ===
def collect_news_articles():
    print("\n" + "="*50)
    print("TASK 2: Thu thập bài viết hướng dẫn")
    print("="*50)
    
    news_urls = [
        {
            "url": "https://en.wikipedia.org/wiki/Probation_(employment)",
            "filename": "article_01_probation.json",
            "title": "Probation in Employment"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Overtime",
            "filename": "article_02_overtime.json",
            "title": "Overtime Regulations"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Worker%27s_compensation",
            "filename": "article_03_worker-compensation.json",
            "title": "Worker's Compensation"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Employment_termination",
            "filename": "article_04_termination.json",
            "title": "Employment Termination"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Parental_leave",
            "filename": "article_05_parental-leave.json",
            "title": "Parental Leave"
        },
        {
            "url": "https://en.wikipedia.org/wiki/Annual_leave",
            "filename": "article_06_annual-leave.json",
            "title": "Annual Leave"
        },
    ]
    
    count = 0
    for item in news_urls:
        print(f"\n[{count+1}/{len(news_urls)}] {item['title']}")
        data = crawl_url(item['url'])
        if data.get('content_markdown') and len(data.get('content_markdown', '')) > 200:
            filepath = NEWS_DIR / item['filename']
            save_json(data, filepath)
            count += 1
    
    print(f"\n✓ Task 2: {count} bài viết")
    return count


def main():
    print("="*60)
    print("FILEFLOW - THU THẬP DỮ LIỆU")
    print("="*60)
    
    legal_count = collect_legal_documents()
    news_count = collect_news_articles()
    
    print("\n" + "="*60)
    print("TỔNG KẾT")
    print("="*60)
    
    legal_files = list(LEGAL_DIR.glob("*.json"))
    news_files = list(NEWS_DIR.glob("*.json"))
    
    print(f"  legal/: {len(legal_files)} files")
    for f in legal_files:
        print(f"    - {f.name}")
    print(f"  news/: {len(news_files)} files")
    for f in news_files:
        print(f"    - {f.name}")
    
    if len(legal_files) >= 3 and len(news_files) >= 5:
        print("\n✓ CP1 PASS: Đủ dữ liệu")
    else:
        print(f"\n⚠ Cần thêm: {max(0, 3-len(legal_files))} legal, {max(0, 5-len(news_files))} news")


if __name__ == "__main__":
    main()
