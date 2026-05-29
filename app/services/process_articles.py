from app.database.repoisitory import get_all_articles_without_markdown, update_article_markdown
from app.database.models import ArticleSchema
from app.scrapers.article import ArticleScraper
import pprint
import os

current_path = os.getcwd()
print(current_path)

def process_articles():
    articles: list[ArticleSchema] = get_all_articles_without_markdown()
    pprint.pprint(articles)

    for article in articles:
        # Now you can use url_to_mark_down without creating an instance
        markdown = ArticleScraper.url_to_mark_down(article.url)
        if markdown:
            update_article_markdown(guid=article.guid, markdown=markdown)
            print(f"Processed article: {article.title}")
            # Do something with the markdown content
        else:
            print(f"Failed to convert article: {article.title}")

if __name__ == "__main__":
    process_articles()

