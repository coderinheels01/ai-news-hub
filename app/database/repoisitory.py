from app.scrapers.youtube_scraper import YouTubeVideo
from app.scrapers.article import Article

from app.database.models import YouTubeVideoSchema, ArticleSchema
from app.database.connection import db_connection
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.orm import Session
from sqlalchemy.engine.cursor import CursorResult
import pprint
import os


def bulk_insert_youtube_videos(videos: list[YouTubeVideo]):
    with db_connection.get_session() as session:
        statement: Insert = insert(YouTubeVideoSchema).values([v.model_dump() for v in videos])
        statement: Insert = statement.on_conflict_do_nothing(index_elements=['video_id'])
        result: CursorResult = session.execute(statement)
        session.commit()
        print("---result---")
        print(f"{result.rowcount} rows inserted")
        return result

def bulk_insert_articles(articles: list[Article]):
    with db_connection.get_session() as session:
        statement: Insert = insert(ArticleSchema).values([a.model_dump() for a in articles])
        statement: Insert = statement.on_conflict_do_nothing(index_elements=['guid'])
        result = session.execute(statement)
        session.commit()
        print("---result---")
        print(f"{result.rowcount} rows inserted")
        return result

def update_article_markdown(guid: str, markdown:str) -> bool:
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
        return session.query(ArticleSchema).filter_by(markdown = None).all()

def update_youtube_transcript(video_id: str, transcript:str):
    with db_connection.get_session() as session:
        video = session.query(YouTubeVideoSchema).filter_by(video_id=video_id).first()
        if video:
            video.transcript = transcript
            session.commit()
            return True
    return False
    
def get_all_youtube_videos_without_markdown() -> list[YouTubeVideoSchema]:
    with db_connection.get_session() as session:
        return session.query(YouTubeVideoSchema).filter_by(transcript = None).all()

