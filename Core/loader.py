# Core/loader.py

import re
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
    """
    video_id = extract_video_id(url)
    ytt_api = YouTubeTranscriptApi()

    try:
        fetched = ytt_api.fetch(video_id, languages=["en"])
    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No English transcript found for this video.")

    # fetched.to_raw_data() -> list of {"text", "start", "duration"} dicts
    full_text = " ".join(snippet["text"] for snippet in fetched.to_raw_data())
    return full_text


if __name__ == "__main__":
    # quick manual test
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    text = get_transcript(test_url)
    print(text[:500])
    print(f"\n--- total characters: {len(text)} ---")