import pprint
from datetime import datetime, timedelta, timezone
from time import time

import feedparser
from feedparser import FeedParserDict
from pydantic import BaseModel


class Article(BaseModel):
    title: str
    description: str | None
    url: str
    guid: str
    published_at: datetime
    category: list[str] | None = None


class ArticleScraper:
    def __init__(self, rss_urls: list[str]):
        self.rss_urls = rss_urls

    def get_articles(self, hours: int = 24) -> list[Article]:
        articles: list[Article] = []

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        for rss_url in self.rss_urls:
            feed: FeedParserDict = feedparser.parse(rss_url)

            for entry in feed.entries:
                published_parsed = entry.get("published_parsed", None)

                if not published_parsed:
                    continue

                published_time: datetime = datetime(
                    *published_parsed[:6], tzinfo=timezone.utc
                )

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
    articles = article_scraper.get_articles(hours=24)
    print("---DONE---")
    print(f"Found {len(articles)} articles")
    for article in articles:
        pprint.pprint(article)
