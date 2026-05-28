import os
import pprint

from docling.document_converter import DocumentConverter

from app.scrapers.article import Article, ArticleScraper


class AnthropicArticleScraper(ArticleScraper):
    def __init__(self):
        super().__init__(
            rss_urls=[
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
            ]
        )
        self.document_converter = DocumentConverter()

    def url_to_mark_down(self, url: str) -> list[str] | None:
        try:
            result = self.document_converter.convert(url)  # noqa: E117
            return result.document.export_to_markdown()
        except Exception:
            return None

    def get_articles(self, hours: int =24) -> list[Article]:
        return super().get_articles(hours=hours, source="Anthropic")
