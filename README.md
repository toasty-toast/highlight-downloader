# Highllight Downloader

## Background

The NBC Sports YouTube channel uploads the best Premier League highlight videos. The only problem is that they upload too much other junk to make subscribing to the channel an option, and remembering to check manually is a pain.

The Highlight Downloader continuously checks the channel for new Premier League highlight videos and downloads them.

## Docker

The tool is best run via Docker, where it can happily churn in the background downloading new videos. The image is available from [Docker Hub](https://hub.docker.com/repository/docker/toastytoast/highlight-downloader).

Only two things are required to run the container.
1. A YouTube API key (you can get this for free in just a few steps)
1. The directory where you want to download the videos, which will be mapped to the `/downloads/` directory in the container.

This is a sample command for starting the container.

```bash
docker run \
    --rm \
    -d \
    -it \
    --env YOUTUBE_DATA_API_KEY="YOUR_KEY" \
    -v "/path/to/my/downloads/":"/downloads":"rw" \
    toastytoast/highlight-downloader
```