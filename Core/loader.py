# Core/loader.py

import os
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url: str) -> str:
    """Pulls the 11-character video ID out of a YouTube URL."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",   # watch?v=... or /embed/...
        r"youtu\.be\/([0-9A-Za-z_-]{11})",   # youtu.be/...
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a video ID from URL: {url}")


def get_transcript(url: str) -> str:
    """
    Fetches the transcript for a YouTube video and returns it as
    a single plain-text string.

    If PROXY_URL is set in environment/secrets, requests are routed
    through that proxy — required on cloud platforms where YouTube
    blocks datacenter IPs.
    """
    video_id = extract_video_id(url)

    proxy_url = os.getenv("PROXY_URL")

    if proxy_url:
        # youtube-transcript-api 1.2.4 accepts an http_client (requests.Session)
        session = requests.Session()
        session.proxies = {"http": proxy_url, "https": proxy_url}
        ytt_api = YouTubeTranscriptApi(http_client=session)
    else:
        ytt_api = YouTubeTranscriptApi()

    try:
        fetched = ytt_api.fetch(video_id, languages=["en"])
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No English transcript found for this video.")
    except Exception as e:
        error_msg = str(e)
        if "IP" in error_msg or "blocked" in error_msg.lower() or "Could not retrieve" in error_msg:
            raise RuntimeError(
                "YouTube is blocking requests from this server's IP. "
                "Update the PROXY_URL secret in Streamlit Cloud settings."
            )
        raise RuntimeError(f"Failed to fetch transcript: {e}")

    full_text = " ".join(snippet["text"] for snippet in fetched.to_raw_data())
    return full_text


if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    text = get_transcript(test_url)
    print(text[:500])
    print(f"\n--- total characters: {len(text)} ---")