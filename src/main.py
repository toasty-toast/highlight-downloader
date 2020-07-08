#!/usr/bin/env python3

from collections import namedtuple
from datetime import date, timedelta
import os
import re
import sys
import time

from googleapiclient.discovery import build
import schedule
import youtube_dl

from silent_logger import SilentLogger

Video = namedtuple("Video", "video_id video_title download_file")

RUN_INTERVAL = 20
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
NBC_SPORTS_CHANNEL_ID = "UCqZQlzSHbVJrwrn5XvzrzcA"
DOWNLOAD_LOCATION = "/downloads"
VIDEO_FILE_EXT = "mp4"


def main():
    print(f"Scheduling downloads to run every {RUN_INTERVAL} minutes")
    run_download_wrapper()
    schedule.every(RUN_INTERVAL).minutes.do(run_download_wrapper)
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_file_for_video(name):
    match = re.match(
        r"(.*) v. (.*) \| PREMIER LEAGUE HIGHLIGHTS \| (.*) \| NBC Sports", name)
    if match is None:
        return name
    team1 = match.group(1)
    team2 = match.group(2)
    date = match.group(3)
    date = date.replace("/", "-")
    return f"{date} - {team1} vs {team2}.{VIDEO_FILE_EXT}"


def run_download_wrapper():
    try:
        run_download()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def run_download():
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY")
    if api_key is None:
        print("Missing environment variable YOUTUBE_DATA_API_KEY", file=sys.stderr)

    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=api_key)

    response = youtube.search().list(
        q="PREMIER LEAGUE HIGHLIGHTS",
        channelId=NBC_SPORTS_CHANNEL_ID,
        type="video",
        order="date",
        part="id,snippet",
        maxResults=50
    ).execute()

    videos = []
    for result in response.get("items", []):
        title = result["snippet"]["title"]
        id = result["id"]["videoId"]
        if "| PREMIER LEAGUE HIGHLIGHTS |" in title:
            video_file = get_file_for_video(title)
            if not os.path.isfile(os.path.join(DOWNLOAD_LOCATION, video_file)):
                print(f"Found new video \"{title}\"")
                videos.append(Video(id, title, video_file))

    for video in videos:
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        print(f"Downloading {video.video_title}")
        download_options = {
            "format": f"bestvideo[ext={VIDEO_FILE_EXT}]+bestaudio",
            "outtmpl": os.path.join(DOWNLOAD_LOCATION, video.download_file),
            "logger": SilentLogger()
        }
        with youtube_dl.YoutubeDL(download_options) as ydl:
            ydl.download([video_url])


if __name__ == "__main__":
    main()
