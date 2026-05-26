import os
import sys
import pprint

current_path = f"{os.getcwd()}/app"
sys.path.append(current_path)

from scrapers.anthropic_scraper import AnthropicArticleScraper
from scrapers.openai_scraper import OpenAIArticleScraper
from scrapers.article import Article

if __name__ == "__main__":
    openai_article_scraper = OpenAIArticleScraper()
    articles: list[Article] = openai_article_scraper.get_articles(hours=48)
    pprint.pprint(articles)
    anthropic_article_scraper = AnthropicArticleScraper()
    articles: list[Article] = anthropic_article_scraper.get_articles(hours=48)
    pprint.pprint(articles)
