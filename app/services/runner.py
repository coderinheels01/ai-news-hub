import sys
import os
import pprint

from app.scrapers.anthropic_scraper import AnthropicArticleScraper
from app.scrapers.openai_scraper import OpenAIArticleScraper

from app.scrapers.youtube_scraper import YouTubeScraper, YouTubeVideo
from config import YOUTUBE_CHANNELS


from app.scrapers.youtube_scraper import YouTubeScraper, YouTubeVideo
from config import YOUTUBE_CHANNELS
from app.database.repoisitory import bulk_insert_youtube_videos, bulk_insert_articles
def run_scrapers():
    youtube_scraper = YouTubeScraper()
    videos: list[YouTubeVideo] = []
    for channel in YOUTUBE_CHANNELS:
        result: list[YouTubeVideo] = youtube_scraper._get_latest_videos(channel_id=channel, hours=48)
        videos=[*videos, *result]

    bulk_insert_youtube_videos(videos)

    print(f"DEBUG: found ${len(videos)} youtube videos")

    anthropic_scraper = AnthropicArticleScraper()
    anthropic_articles = anthropic_scraper.get_articles(hours=150)
    pprint.pprint(f"DEBUG: found ${len(anthropic_articles)} anthropic articles")
    bulk_insert_articles(articles=anthropic_articles)


    openai_scraper = OpenAIArticleScraper()
    openai_articles = openai_scraper.get_articles(hours=150)
    print(f"DEBUG: found ${len(openai_articles)} openai articles")
    bulk_insert_articles(articles=openai_articles)

if __name__ == "__main__":
    run_scrapers()

import os
print(os.getcwd())