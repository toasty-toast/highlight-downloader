FROM python:3.8-slim-buster AS base

FROM base AS builder

RUN apt-get update -y && \
    apt-get install -y gcc zlib1g-dev libjpeg-dev && \
    apt-get clean

COPY requirements.txt .
RUN python -m pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt

FROM base as final

WORKDIR /app
RUN mkdir -p /downloads
ENV YOUTUBE_DATA_API_KEY ""

COPY --from=builder /usr/local/lib/python3.8/ /usr/local/lib/python3.8/
COPY src/*.py ./
