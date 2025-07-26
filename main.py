# path: main.py

import time
import sys
from src.news_fetcher import fetch_new_article_links, fetch_article
from src.ai_processor import is_article_safe, generate_reading_material
from src.supabase_uploader import upload_material, clean_original_content
from src.persistence import load_processed_urls, save_processed_url
from src.rss_feeds import FEEDS

# --- Configuration ---
# Check for new articles every 30 minutes.
# You can adjust this value as needed.
CHECK_INTERVAL_SECONDS = 30 * 60

def process_single_article(url: str, source: str):
    """Runs the full pipeline for a single article."""
    try:
        # 1. Fetch the article content
        article = fetch_article(url)
        if not article or not article.get('content'):
            print(f"⚠️  Could not fetch or content is empty for article: {url}", file=sys.stderr)
            return

        # 2. Perform safety check
        if not is_article_safe(article['title'], article['content']):
            save_processed_url(url) # Mark as processed even if unsafe to avoid re-checking
            return # Stop processing if unsafe

        # 3. Generate the reading material
        material_json = generate_reading_material(article['title'], article['content'], url)

        # 4. Upload to Supabase, including original content
        upload_material(
            material_data=material_json, 
            original_link=url,
            original_content=article['content']
        )

    # --- 健壮性修复 ---
    # 捕获所有可能的异常，以确保单个文章的失败不会中断整个循环。
    except Exception as e:
        print(f"❌ Failed to process article {url}: {e}", file=sys.stderr)
    # --- 修复结束 ---

def main_loop():
    """The main continuous loop of the autoMag service."""
    print("🚀 autoMag service started. Press Ctrl+C to stop.")
    processed_urls = load_processed_urls()
    print(f"Loaded {len(processed_urls)} previously processed URLs.")

    while True:
        print("\n---")
        print(f"Starting new cycle at {time.ctime()}...")
        new_articles_found = 0

        for source, feed_url in FEEDS.items():
            print(f"🔍 Checking feed: {feed_url}")
            try:
                links = fetch_new_article_links(feed_url)
                new_links = [link for link in links if link not in processed_urls]

                if new_links:
                    print(f"Found {len(new_links)} new articles from {source}.")
                    for link in new_links:
                        # 此处检查是为了防止在循环内部添加后再次处理
                        if link in processed_urls:
                            continue
                        
                        print(f"\nProcessing new article: {link}")
                        process_single_article(link, source)
                        
                        # 无论成功或失败，都将其标记为已处理，防止重试
                        processed_urls.add(link)
                        save_processed_url(link)
                        
                        new_articles_found += 1
                else:
                    print(f"No new articles from {source}.")

            except Exception as e:
                print(f"Could not process feed {source}: {e}", file=sys.stderr)

        print("\nCycle finished.")
        print(f"Processed {new_articles_found} new articles in this cycle.")
        print(f"Waiting for {CHECK_INTERVAL_SECONDS / 60} minutes until the next cycle...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user.")
        sys.exit(0)