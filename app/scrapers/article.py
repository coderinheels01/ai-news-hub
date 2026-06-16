import pprint
from datetime import UTC, datetime, timedelta

import feedparser
import requests
from feedparser import FeedParserDict
from html_to_markdown import convert
from pydantic import BaseModel


class Article(BaseModel):
    title: str
    description: str | None
    source: str
    url: str
    guid: str
    published_at: datetime
    category: list[str] | None = None


class ArticleScraper:
    def __init__(self, rss_urls: list[str]):
        self.rss_urls = rss_urls

    def url_to_markdown(self, url: str) -> str | None:
        try:
            response = requests.get(
                url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30
            )
            response.raise_for_status()
            html = response.text
            markdown = convert(html)
            return markdown
        except Exception:
            return None

    def get_articles(self, source: str, hours: int = 24) -> list[Article]:
        articles: list[Article] = []

        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

        for rss_url in self.rss_urls:
            feed: FeedParserDict = feedparser.parse(rss_url)

            print("=== entries ===")
            pprint.pprint(feed.entries)
            for entry in feed.entries:
                published_parsed = entry.get("published_parsed", None)

                if not published_parsed:
                    continue

                published_time: datetime = datetime(*published_parsed[:6], tzinfo=UTC)

                if published_time >= cutoff_time:
                    # Get category from tags if available
                    tags = entry.get("tags", [])
                    category = None
                    if tags and len(tags) > 0:
                        first_tag = tags[0]
                        category = (
                            [first_tag.get("term")] if first_tag.get("term") else None
                        )

                    article: Article = Article(
                        title=entry.get("title"),
                        source=source,
                        description=entry.get("summary"),
                        url=entry.get("link"),
                        guid=entry.get("id", entry.get("link", "")),
                        published_at=published_time,
                        category=category,
                    )
                    articles.append(article)

        return articles


if __name__ == "__main__":
    article_scraper = ArticleScraper(["https://openai.com/news/rss.xml"])
    articles = article_scraper.get_articles(hours=24, source="OpenAI")
    print("---DONE---")
    print(f"Found {len(articles)} articles")
    for article in articles:
        pprint.pprint(article)
