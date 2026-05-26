import os
import pprint

from scrapers.article import Article, ArticleScraper


class AnthropicArticleScraper(ArticleScraper):
    def __init__(self):
        super().__init__(
            rss_urls=[
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml",
                "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
            ]
        )
