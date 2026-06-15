from app.agent.digest_agent import DigestAgent, DigestAgentResponse
from app.database.models import DigestSchema
from app.database.repoisitory import (
    NormalizedArticle,
    get_undigested_articles,
    insert_digest,
)

digest_agent = DigestAgent()


def process_digests():
    undigested_articles: list[NormalizedArticle] = get_undigested_articles()
    for a in undigested_articles:
        digest_response: DigestAgentResponse = digest_agent.generate_digest(
            title=a.title, article_type=a.article_type, content=a.content
        )
        digest_id = f"{a.article_type}:{a.article_id}"

        digest_schema = DigestSchema(
            id=digest_id,
            article_id=a.article_id,
            article_type=a.article_type,
            title=digest_response.title,
            url=a.url,
            summary=digest_response.summary,
        )
        insert_digest(digest_schema)


if __name__ == "__main__":
    process_digests()
