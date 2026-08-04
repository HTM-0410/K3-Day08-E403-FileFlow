"""
Task 3: Convert JSON sang Markdown trong standardized/
"""

import json
from pathlib import Path


def convert_json_to_markdown():
    DATA_DIR = Path(__file__).parent.parent / "data"
    LANDING_LEGAL = DATA_DIR / "landing" / "legal"
    LANDING_NEWS = DATA_DIR / "landing" / "news"
    STANDARDIZED_LEGAL = DATA_DIR / "standardized" / "legal"
    STANDARDIZED_NEWS = DATA_DIR / "standardized" / "news"
    
    STANDARDIZED_LEGAL.mkdir(parents=True, exist_ok=True)
    STANDARDIZED_NEWS.mkdir(parents=True, exist_ok=True)
    
    def json_to_markdown(json_path: Path, output_dir: Path) -> bool:
        try:
            data = json.loads(json_path.read_text(encoding='utf-8'))
            
            # Tạo filename từ title
            title = data.get('title', 'untitled')
            safe_name = title.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')[:50]
            md_file = output_dir / f"{safe_name}.md"
            
            # Tạo markdown
            md_content = f"""---
title: {data.get('title', '')}
source: {data.get('source', '')}
url: {data.get('url', '')}
date_crawled: {data.get('date_crawled', '')}
description: {data.get('description', '')}
---

# {data.get('title', 'Untitled')}

{data.get('content_markdown', '')}

---
*Source: {data.get('url', '')}*
*Date crawled: {data.get('date_crawled', '')}*
"""
            
            md_file.write_text(md_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"  ERROR {json_path.name}: {e}")
            return False
    
    print("="*50)
    print("TASK 3: Convert JSON sang Markdown")
    print("="*50)
    
    # Convert legal
    print("\n[Legal documents]")
    legal_count = 0
    for f in LANDING_LEGAL.glob("*.json"):
        if json_to_markdown(f, STANDARDIZED_LEGAL):
            print(f"  ✓ {f.stem}.md")
            legal_count += 1
    
    # Convert news
    print("\n[News articles]")
    news_count = 0
    for f in LANDING_NEWS.glob("*.json"):
        if json_to_markdown(f, STANDARDIZED_NEWS):
            print(f"  ✓ {f.stem}.md")
            news_count += 1
    
    print(f"\n✓ Task 3 hoàn thành:")
    print(f"  legal: {legal_count} files in standardized/legal/")
    print(f"  news: {news_count} files in standardized/news/")
    print(f"  Tổng: {legal_count + news_count} files")
    
    # List files
    print("\nFiles created:")
    print("  standardized/legal/:")
    for f in STANDARDIZED_LEGAL.glob("*.md"):
        print(f"    - {f.name}")
    print("  standardized/news/:")
    for f in STANDARDIZED_NEWS.glob("*.md"):
        print(f"    - {f.name}")
    
    return legal_count, news_count


if __name__ == "__main__":
    convert_json_to_markdown()
