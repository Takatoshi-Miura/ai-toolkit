#!/usr/bin/env python3
"""
Yahoo ニュースを取得して Issue 用の Markdown を生成するスクリプト
BeautifulSoup を使用した完全無料版（API 不要）
"""

import sys
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    """指定URLのHTMLを取得"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def extract_news_from_html(html: str, category: str) -> List[Dict[str, str]]:
    """BeautifulSoupを使ってHTMLからニュース記事を抽出"""

    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    # Yahoo ニュースの記事リンクを抽出
    # 複数のパターンを試行して記事を取得

    # パターン1: <a> タグで href に '/articles/' が含まれるもの
    links = soup.find_all('a', href=lambda x: x and '/articles/' in x)

    seen_urls = set()

    for link in links:
        href = link.get('href', '')

        # 完全なURLに変換
        if href.startswith('/'):
            url = f'https://news.yahoo.co.jp{href}'
        elif not href.startswith('http'):
            continue
        else:
            url = href

        # 重複チェック
        if url in seen_urls:
            continue

        # タイトルを取得（複数の方法を試行）
        title = None

        # 方法1: aria-label 属性
        if link.get('aria-label'):
            title = link.get('aria-label')

        # 方法2: リンク内のテキスト
        if not title:
            title = link.get_text(strip=True)

        # 方法3: 親要素から取得
        if not title or len(title) < 10:
            parent = link.find_parent(['li', 'div', 'article'])
            if parent:
                # 見出しタグを探す
                heading = parent.find(['h1', 'h2', 'h3', 'h4'])
                if heading:
                    title = heading.get_text(strip=True)

        # タイトルが有効な場合のみ追加
        if title and len(title) >= 10 and url.startswith('https://news.yahoo.co.jp/articles/'):
            articles.append({
                'title': title,
                'url': url
            })
            seen_urls.add(url)

            # 8件取得したら終了
            if len(articles) >= 8:
                break

    # 8件に満たない場合、別のパターンも試行
    if len(articles) < 8:
        # パターン2: data-cl-params 属性を持つリンク（Yahoo特有の属性）
        additional_links = soup.find_all('a', attrs={'data-cl-params': True})

        for link in additional_links:
            if len(articles) >= 8:
                break

            href = link.get('href', '')

            if '/articles/' not in href:
                continue

            if href.startswith('/'):
                url = f'https://news.yahoo.co.jp{href}'
            else:
                url = href

            if url in seen_urls:
                continue

            # タイトル取得
            title = link.get_text(strip=True)

            if not title or len(title) < 10:
                continue

            articles.append({
                'title': title,
                'url': url
            })
            seen_urls.add(url)

    return articles[:8]  # 最大8件


def generate_markdown(domestic_articles, world_articles, business_articles) -> str:
    """Issue用のMarkdownを生成"""

    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")

    md = f"""# 📰 Yahoo ニュースまとめ - {date_str}

> 自動取得日時: {now.strftime("%Y-%m-%d %H:%M:%S")}

---

## 🏠 国内ニュース

"""

    # 国内タイトル
    for i, article in enumerate(domestic_articles[:8], 1):
        md += f"{i}. {article['title']}\n"

    md += "\n## 🌏 国際ニュース\n\n"

    # 国際タイトル
    for i, article in enumerate(world_articles[:8], 1):
        md += f"{i}. {article['title']}\n"

    md += "\n## 💼 経済ニュース\n\n"

    # 経済タイトル
    for i, article in enumerate(business_articles[:8], 1):
        md += f"{i}. {article['title']}\n"

    md += "\n---\n\n## 🔗 リンク集\n\n### 国内\n"

    # リンク集
    for i, article in enumerate(domestic_articles[:8], 1):
        md += f"{i}. [{article['title']}]({article['url']})\n"

    md += "\n### 国際\n"
    for i, article in enumerate(world_articles[:8], 1):
        md += f"{i}. [{article['title']}]({article['url']})\n"

    md += "\n### 経済\n"
    for i, article in enumerate(business_articles[:8], 1):
        md += f"{i}. [{article['title']}]({article['url']})\n"

    md += "\n---\n\n"
    md += "*このIssueは GitHub Actions により自動生成されました（完全無料版）*\n"

    return md


def main():
    """メイン処理"""

    # 各カテゴリのURL
    categories = {
        'domestic': 'https://news.yahoo.co.jp/categories/domestic',
        'world': 'https://news.yahoo.co.jp/categories/world',
        'business': 'https://news.yahoo.co.jp/categories/business'
    }

    print("📡 Fetching Yahoo News (完全無料版)...")

    # 各カテゴリのニュースを取得
    results = {}

    for category_key, url in categories.items():
        print(f"  - Fetching {category_key}...")
        try:
            html = fetch_html(url)
            articles = extract_news_from_html(html, category_key)
            results[category_key] = articles
            print(f"    ✓ Found {len(articles)} articles")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results[category_key] = []

    # 記事が1件も取得できなかった場合はエラー
    total_articles = sum(len(v) for v in results.values())
    if total_articles == 0:
        print("\n❌ Error: No articles found. Yahoo may have changed their HTML structure.")
        sys.exit(1)

    # Markdown を生成
    print("\n📝 Generating Markdown...")
    markdown = generate_markdown(
        results.get('domestic', []),
        results.get('world', []),
        results.get('business', [])
    )

    # ファイルに保存
    output_file = 'news_output.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✅ News saved to {output_file}")
    print(f"\nTotal articles: {total_articles}")


if __name__ == '__main__':
    main()
