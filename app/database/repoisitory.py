from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.engine.cursor import CursorResult

from app.database.connection import db_connection
from app.database.models import ArticleSchema, DigestSchema, YouTubeVideoSchema
from app.scrapers.article import Article
from app.scrapers.youtube_scraper import YouTubeVideo


class NormalizedArticle(BaseModel):
    article_id: str
    article_type: str
    content: str
    title: str
    published_at: datetime
    url: str


class Digest(BaseModel):
    id: str
    article_id: str
    article_type: str
    url: str
    title: str
    summary: str
    created_at: datetime


def bulk_insert_youtube_videos(videos: list[YouTubeVideo]):
    if not videos:
        print("No videos to insert, skipping")
        return None
    with db_connection.get_session() as session:
        statement: Insert = insert(YouTubeVideoSchema).values(
            [v.model_dump() for v in videos]
        )
        statement: Insert = statement.on_conflict_do_nothing(
            index_elements=["video_id"]
        )
        result: CursorResult = session.execute(statement)
        session.commit()
        print("---result---")
        print(f"{result.rowcount} rows inserted")
        return result


def bulk_insert_articles(articles: list[Article]):
    if not articles:
        print("No articles to insert, skipping")
        return None
    with db_connection.get_session() as session:
        statement: Insert = insert(ArticleSchema).values(
            [a.model_dump() for a in articles]
        )
        statement: Insert = statement.on_conflict_do_nothing(index_elements=["guid"])
        result = session.execute(statement)
        session.commit()
        print("---result---")
        print(f"{result.rowcount} rows inserted")
        return result


def insert_digest(digest: DigestSchema):
    if not digest:
        print("No digest to insert, skipping")
        return None
    with db_connection.get_session() as session:
        try:
            session.add(digest)
            session.commit()
            print(f"DEBUG: digest with id {digest.id} inserted")
        except Exception:
            session.rollback()
            print(f"DEBUG: digest with id {digest.id} already exists, skipping")


def update_article_markdown(guid: str, markdown: str) -> bool:
    """Update the article markdown file with the new video"""
    with db_connection.get_session() as session:
        article = session.query(ArticleSchema).filter_by(guid=guid).first()
        if article:
            article.markdown = markdown
            session.commit()
            return True
    return False


def get_all_articles_without_markdown() -> list[ArticleSchema]:
    with db_connection.get_session() as session:
        return session.query(ArticleSchema).filter_by(markdown=None).all()


def update_youtube_transcript(video_id: str, transcript: str):
    with db_connection.get_session() as session:
        video = session.query(YouTubeVideoSchema).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            session.commit()
            return True
    return False


def get_all_youtube_videos_without_markdown() -> list[YouTubeVideoSchema]:
    with db_connection.get_session() as session:
        return session.query(YouTubeVideoSchema).filter_by(transcript=None).all()


def get_undigested_articles(limit: int | None = None) -> list[NormalizedArticle]:
    with db_connection.get_session() as session:
        undigested_articles: list[NormalizedArticle] = []

        videos: list[YouTubeVideoSchema] = (
            session.query(YouTubeVideoSchema)
            .filter(
                YouTubeVideoSchema.transcript.isnot(None),
                YouTubeVideoSchema.transcript != "__UNAVAILABLE__",
            )
            .all()
        )

        print(f"DEBUG: {len(videos)} videos found")

        for video in videos:
            undigested_articles.append(
                NormalizedArticle(
                    article_id=video.video_id,
                    article_type="youtube",
                    url=video.url,
                    content=video.transcript or video.description or "",
                    title=video.title,
                    published_at=video.published_at,
                )
            )
        articles: list[ArticleSchema] = (
            session.query(ArticleSchema)
            .filter(
                or_(
                    ArticleSchema.source == "OpenAI",
                    and_(
                        ArticleSchema.source == "Anthropic",
                        ArticleSchema.markdown.isnot(None),
                    ),
                )
            )
            .all()
        )

        print(f"DEBUG: {len(articles)} articles found")

        for article in articles:
            undigested_articles.append(
                NormalizedArticle(
                    article_id=article.guid,
                    article_type=article.source,
                    url=article.url,
                    content=article.markdown or article.description or "",
                    title=article.title,
                    published_at=article.published_at,
                )
            )

        return undigested_articles


def get_recent_digests(hours: int = 24) -> list[Digest]:
    cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

    with db_connection.get_session() as session:
        digests = (
            session.query(DigestSchema)
            .filter(DigestSchema.created_at >= cutoff_time)
            .order_by(DigestSchema.created_at.desc())
            .all()
        )

    return [
        Digest(
            id=d.id,
            article_type=d.article_type,
            article_id=d.article_id,
            url=d.url,
            title=d.title,
            summary=d.summary,
            created_at=d.created_at,
        )
        for d in digests
    ]
