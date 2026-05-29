import os
import sys
import pprint

current_path = f"{os.getcwd()}/app"
sys.path.append(current_path)

from scrapers.anthropic_scraper import AnthropicArticleScraper
from scrapers.openai_scraper import OpenAIArticleScraper
from scrapers.article import Article, ArticleScraper

if __name__ == "__main__":
    openai_article_scraper = OpenAIArticleScraper()
    open_ai_articles: list[Article] = openai_article_scraper.get_articles(hours=48)
    pprint.pprint(open_ai_articles)
    anthropic_article_scraper = AnthropicArticleScraper()
    anthropic_articles: list[Article] = anthropic_article_scraper.get_articles(hours=48)
    pprint.pprint(anthropic_articles)
    if len(anthropic_articles) > 0:
        markdown: str = ArticleScraper.url_to_mark_down(anthropic_articles[0].url)
        print(markdown)

