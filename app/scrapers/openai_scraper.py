from app.scrapers.article import Article, ArticleScraper


class OpenAIArticleScraper(ArticleScraper):
    def __init__(self):
        # Initialize the parent class with OpenAI's RSS feed URL
        super().__init__(rss_urls=["https://openai.com/news/rss.xml"])

    def get_articles(self, hours: int =24) -> list[Article]:
        return super().get_articles(hours=hours, source="OpenAI")
