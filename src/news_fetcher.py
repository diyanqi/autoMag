import requests
import feedparser
from bs4 import BeautifulSoup

def fetch_new_article_links(feed_url: str) -> list[str]:
    """
    Parses an RSS feed and returns a list of article links.

    Args:
        feed_url: The URL of the RSS feed.

    Returns:
        A list of URLs for the articles in the feed.
    """
    print(f"🔍 Checking feed: {feed_url}")
    feed = feedparser.parse(feed_url)
    return [entry.link for entry in feed.entries]


def fetch_article(url: str) -> dict:
    """
    从给定的URL抓取新闻标题和正文内容。

    Args:
        url: 新闻文章的URL。

    Returns:
        一个包含'title'和'content'的字典。
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # 如果请求失败则抛出异常

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取标题
        title_tag = soup.find('h1') or soup.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else "无法提取标题"

        # 提取正文内容 (这是一个通用尝试，可能需要为特定网站调整)
        # 优先寻找 <article> 标签，其次是 <main>
        article_body = soup.find('article') or soup.find('main')
        
        if not article_body:
            # 如果找不到，就退而求其次，获取所有 <p> 标签的内容
            paragraphs = soup.find_all('p')
        else:
            paragraphs = article_body.find_all('p')

        content_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        if not content_text:
             raise ValueError("无法从页面提取到有效的段落内容。")

        print(f"✅ 成功抓取文章: {title_text}")
        # print(content_text)
        return {
            'title': title_text,
            'content': content_text,
            'original_link': url
        }

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"抓取文章失败: 网络错误 - {e}")
    except Exception as e:
        raise RuntimeError(f"解析文章时发生未知错误: {e}")
