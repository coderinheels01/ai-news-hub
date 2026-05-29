import pprint
from app.database.repoisitory import get_all_youtube_videos_without_markdown, update_youtube_transcript
from app.scrapers.youtube_scraper import YouTubeScraper

import os
current_dir = os.getcwd()
current_dir

def prcess_youtube_transcript():
    videos: list[YouTubeVideoSchema] = get_all_youtube_videos_without_markdown()
    pprint.pprint(videos)
    scraper = YouTubeScraper()
    for video in videos:
        transcript:YouTubeTranscript = scraper._get_transcript(video_id=video.video_id)
        update_youtube_transcript(video_id=video.video_id, transcript=transcript.text)
        pass
    pass



if __name__ == "__main__":
    prcess_youtube_transcript()