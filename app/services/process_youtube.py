import logging

from app.database.models import YouTubeVideoSchema
from app.database.repoisitory import (
    get_all_youtube_videos_without_markdown,
    update_youtube_transcript,
)
from app.scrapers.youtube_scraper import YouTubeScraper, YouTubeTranscript

logger = logging.getLogger(__name__)


def process_youtube_transcripts():
    videos: list[YouTubeVideoSchema] = get_all_youtube_videos_without_markdown()
    logger.info(f"Processing transcripts for {len(videos)} videos")
    scraper = YouTubeScraper()
    processed = 0
    unprocessed = 0
    for video in videos:
        transcript: YouTubeTranscript = scraper._get_transcript(video_id=video.video_id)
        if (
            transcript is None
            or transcript.text is None
            or transcript.text == "__UNAVAILABLE__"
        ):
            logger.warning(
                f"No transcript available for {video.video_id}, marking as unavailable"
            )
            update_youtube_transcript(
                video_id=video.video_id, transcript="__UNAVAILABLE__"
            )
            unprocessed += 1
        else:
            update_youtube_transcript(
                video_id=video.video_id, transcript=transcript.text
            )
            processed += 1
    return {"processed": processed, "unprocessed": unprocessed}


if __name__ == "__main__":
    process_youtube_transcripts()
