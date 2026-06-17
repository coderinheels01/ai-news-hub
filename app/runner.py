import logging

from app.database.repoisitory import bulk_insert_articles, bulk_insert_youtube_videos
from app.scrapers.anthropic_scraper import AnthropicArticleScraper
from app.scrapers.openai_scraper import OpenAIArticleScraper
from app.scrapers.youtube_scraper import YouTubeScraper, YouTubeVideo
from config import YOUTUBE_CHANNELS

logger = logging.getLogger(__name__)


def run_scrapers(hours: str = 24):
    youtube_scraper = YouTubeScraper()
    videos: list[YouTubeVideo] = []
    for channel in YOUTUBE_CHANNELS:
        result: list[YouTubeVideo] = youtube_scraper._get_latest_videos(
            channel_id=channel, hours=hours
        )
        videos = [*videos, *result]

    bulk_insert_youtube_videos(videos)

    logger.info(f"Found {len(videos)} youtube videos")

    anthropic_scraper = AnthropicArticleScraper()
    anthropic_articles = anthropic_scraper.get_articles(hours=hours)
    logger.info(f"Found {len(anthropic_articles)} anthropic articles")
    bulk_insert_articles(articles=anthropic_articles)

    openai_scraper = OpenAIArticleScraper()
    openai_articles = openai_scraper.get_articles(hours=hours)
    logger.info(f"Found {len(openai_articles)} openai articles")
    bulk_insert_articles(articles=openai_articles)

    return {
        "youtube": videos,
        "anthropic": anthropic_articles,
        "openai": openai_articles,
    }


if __name__ == "__main__":
    run_scrapers()
