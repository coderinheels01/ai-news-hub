from sqlalchemy import Column, String, DateTime,Text
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

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

