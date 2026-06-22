# Core/loader.py

import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url: str) -> str:
    """Pulls the 11-character video ID out of a YouTube URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a video ID from URL: {url}")


def get_transcript(url: str) -> str:
    """
    Fetches the transcript for a YouTube video.

    Set these in Streamlit Cloud secrets (or .env locally):
        WEBSHARE_USERNAME = "pqcldplc"
        WEBSHARE_PASSWORD = "5bteyedd05gq"
    """
    video_id = extract_video_id(url)

    username = os.getenv("WEBSHARE_USERNAME")
    password = os.getenv("WEBSHARE_PASSWORD")

    if username and password:
        proxy_config = WebshareProxyConfig(
            proxy_username=username,
            proxy_password=password,
            retries_when_blocked=3,
        )
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
    else:
        ytt_api = YouTubeTranscriptApi()

    try:
        fetched = ytt_api.fetch(video_id, languages=["en"])
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No English transcript found for this video.")
    except Exception as e:
        raise RuntimeError(f"Couldn't load transcript: {e}")

    full_text = " ".join(snippet["text"] for snippet in fetched.to_raw_data())
    return full_text


if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    text = get_transcript(test_url)
    print(text[:500])
    print(f"\n--- total characters: {len(text)} ---")