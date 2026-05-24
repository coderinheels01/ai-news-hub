import os
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api import YouTubeTranscriptApi, FetchedTranscript
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import feedparser
from feedparser import FeedParserDict
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import time
from enum import Enum
import pprint


class YouTubeUrlPattern(Enum):
    WATCH = "youtube.com/watch?v="
    SHORTS = "youtube.com/shorts/"
    SHORT_URL = "youtu.be/"


class YouTubeTranscript(BaseModel):
    text: str


class YouTubeVideo(BaseModel):
    title: str
    url: str
    video_id: str
    published_at: datetime
    description: str
    transcript: Optional[str] = None


class YouTubeScraper:
    def __init__(self, rate_limit_per_second: float = 0.2):
        proxy_config: WebshareProxyConfig = None
        proxy_username: str = os.getenv("PROXY_USERNAME")
        proxy_password: str = os.getenv("PROXY_PASSWORD")
        print(f"PROXY_USERNAME: {os.getenv('PROXY_USERNAME')}")
        print(f"PROXY_PASSWORD: {os.getenv('PROXY_PASSWORD')}")

        if proxy_username and proxy_password:
            print("DEBUGGER: using webshare proxy")
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username, proxy_password=proxy_password
            )
        self.youtube_transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        self.last_request: float = 0
        self.rate_limit_per_second = rate_limit_per_second

    def _get_rss_feed_url(self, channel_id: str):
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    def _get_video_id(self, video_link: str) -> str:
        print(f"DEBUG: video_link - {video_link}")
        if YouTubeUrlPattern.WATCH.value in video_link:
            return video_link.split("v=")[1].split("&")[0]
        elif YouTubeUrlPattern.SHORTS.value in video_link:
            return video_link.split("shorts/")[1].split("?")[0]
        elif YouTubeUrlPattern.SHORT_URL.value in video_link:
            return video_link.split("youtu.be/")[1].split("?")[0]
        else:
            return video_link

    def _rate_limit(self):
        min_limit: float = 1 / self.rate_limit_per_second
        current_time: float = time.monotonic()
        duration: float = current_time - self.last_request

        if duration < min_limit:
            time.sleep(min_limit - duration)
        self.last_request = time.monotonic()

    def _get_transcript(self, video_id: str) -> Optional[YouTubeTranscript]:
        try:
            self._rate_limit()
            transcript: FetchedTranscript = self.youtube_transcript_api.fetch(
                video_id=video_id
            )
            text: str = "".join([snippet.text for snippet in transcript.snippets])
            transcript = YouTubeTranscript(text=text)
            return transcript
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(
                f"DEBUG: No transcript exception for video_id - {video_id}- ERROR: {e}"
            )
            return None
        except Exception as e:
            print(f"DEBUG: Exception for video_id - {video_id}- ERROR: {e}")
            return None

    def _get_latest_videos(self, channel_id: str, hours: int) -> list[YouTubeVideo]:
        rss_feed: FeedParserDict = feedparser.parse(
            self._get_rss_feed_url(channel_id=channel_id)
        )
        videos: list[YouTubeVideo] = []
        for entry in rss_feed.entries:
            published_time = datetime(*entry.published_parsed[:6])
            video_id: str = self._get_video_id(entry.link)
            transcript: YouTubeTranscript = self._get_transcript(video_id=video_id)
            pprint.pprint(transcript)
            video = YouTubeVideo(
                title=entry.title,
                url=entry.link,
                video_id=video_id,
                published_at=published_time,
                description=entry.get("summary", ""),
            )
            videos.append(video)

        return videos

    def scrape(self, channel_id: str, hours: int = 150) -> list[YouTubeVideo]:
        return self._get_latest_videos(channel_id=channel_id, hours=hours)


if __name__ == "__main__":
    scraper = YouTubeScraper()
    scraper.scrape(channel_id="UCn8ujwUInbJkBhffxqAPBVQ", hours=24)
