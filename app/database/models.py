from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase


class BaseSchema(DeclarativeBase):
    pass


class YouTubeVideoSchema(BaseSchema):
    __tablename__ = "youtube_videos"
    video_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    description = Column(Text)
    transcript = Column(Text)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ArticleSchema(BaseSchema):
    __tablename__ = "article"
    guid = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    source = Column(String)
    category = Column(String)
    markdown = Column(Text)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DigestSchema(BaseSchema):
    __tablename__ = "digest"
    id = Column(String, primary_key=True)
    article_type = Column(String, nullable=False)
    article_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
