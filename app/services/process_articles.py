import logging

from app.database.models import ArticleSchema
from app.database.repoisitory import (
    get_all_articles_without_markdown,
    update_article_markdown,
)
from app.scrapers.article import ArticleScraper

logger = logging.getLogger(__name__)


def process_articles():
    articles: list[ArticleSchema] = get_all_articles_without_markdown()
    logger.info(f"Processing {len(articles)} articles without markdown")

    for article in articles:
        markdown = ArticleScraper.url_to_mark_down(article.url)
        if markdown:
            update_article_markdown(guid=article.guid, markdown=markdown)
            logger.info(f"Processed article: {article.title}")
        else:
            logger.warning(f"Failed to convert article: {article.title}")


if __name__ == "__main__":
    process_articles()
