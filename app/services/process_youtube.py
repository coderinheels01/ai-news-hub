import pprint

from app.database.models import YouTubeVideoSchema
from app.database.repoisitory import (
    get_all_youtube_videos_without_markdown,
    update_youtube_transcript,
)
from app.scrapers.youtube_scraper import YouTubeScraper, YouTubeTranscript


def process_youtube_transcripts():
    videos: list[YouTubeVideoSchema] = get_all_youtube_videos_without_markdown()
    pprint.pprint(videos)
    scraper = YouTubeScraper()
    processed = 0
    unprocessed = 0
    for video in videos:
        transcript: YouTubeTranscript = scraper._get_transcript(video_id=video.video_id)
        update_youtube_transcript(video_id=video.video_id, transcript=transcript.text)
        if transcript.text == "__UNAVAILABLE__" or transcript.text is None:
            unprocessed += 1
        else:
            processed += 1
    return {"processed": processed, "unprocessed": unprocessed}


if __name__ == "__main__":
    process_youtube_transcripts()
