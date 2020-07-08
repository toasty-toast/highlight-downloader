#!/usr/bin/env python3

from datetime import date, timedelta
import os
import sys
import time

from googleapiclient.discovery import build
import schedule
import youtube_dl

from silent_logger import SilentLogger


RUN_INTERVAL = 20
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
NBC_SPORTS_CHANNEL_ID = 'UCqZQlzSHbVJrwrn5XvzrzcA'


def main():
    print(f'Scheduling downloads to run every {RUN_INTERVAL} minutes')
    run_download()
    schedule.every(RUN_INTERVAL).minutes.do(run_download)
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_download():
    api_key = os.environ.get('YOUTUBE_DATA_API_KEY')
    if api_key is None:
        print('Missing environment variable YOUTUBE_DATA_API_KEY', file=sys.stderr)

    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=api_key)

    response = youtube.search().list(
        q='PREMIER LEAGUE HIGHLIGHTS',
        channelId=NBC_SPORTS_CHANNEL_ID,
        type="video",
        order='date',
        part='id,snippet',
        maxResults=50
    ).execute()

    video_ids = []
    for result in response.get('items', []):
        title = result['snippet']['title']
        id = result['id']['videoId']
        if '| PREMIER LEAGUE HIGHLIGHTS |' in title:
            print(f'Found video "{title}"')
            video_ids.append(id)

    download_options = {
        'download_archive': 'downloaded.txt',
        'format': 'bestvideo[ext=mp4]+bestaudio',
        'outtmpl': '/downloads/%(title)s.%(ext)s',
        'logger': SilentLogger()
    }
    for id in video_ids:
        video_url = f'https://www.youtube.com/watch?v={id}'
        with youtube_dl.YoutubeDL(download_options) as ydl:
            ydl.download([video_url])


if __name__ == "__main__":
    main()
