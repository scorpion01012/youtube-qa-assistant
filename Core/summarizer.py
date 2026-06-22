# Core/summarizer.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

load_dotenv()

SUMMARY_PROMPT = ChatPromptTemplate.from_template(
    """You are summarizing a YouTube video transcript for someone who hasn't
watched it. Write a clear, well-organized summary covering:

1. The main topic / purpose of the video
2. Key points discussed (as a short bulleted list)
3. Any conclusions, takeaways, or calls to action

Transcript:
{transcript}

Summary:"""
)


def build_summarizer(model: str = "claude-sonnet-4-6"):
    llm = ChatAnthropic(model=model, temperature=0)
    chain = SUMMARY_PROMPT | llm | StrOutputParser()
    return chain


def summarize_transcript(transcript: str, model: str = "claude-sonnet-4-6") -> str:
    chain = build_summarizer(model)
    return chain.invoke({"transcript": transcript})


if __name__ == "__main__":
    from loader import get_transcript

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript = get_transcript(test_url)

    summary = summarize_transcript(transcript)
    print(summary)