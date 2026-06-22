# app.py
# streamlit run app.py .use this command to run the app.
import os
import sys
import streamlit as st

# Make the Core/ folder importable
sys.path.append(os.path.join(os.path.dirname(__file__), "Core"))

from loader import get_transcript
from vectorstore import build_vectorstore
from qa_chain import build_qa_chain
from summarizer import summarize_transcript


st.set_page_config(page_title="YouTube RAG Assistant", page_icon="🎬")
st.title("🎬 YouTube Video Summarizer & QA Tool")
st.caption("Powered by LangChain, FAISS, and Claude")

# --- Session state setup ---
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# --- Step 1: Load video ---
url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...")

if st.button("Load Video", type="primary"):
    if not url:
        st.warning("Paste a YouTube URL first.")
    else:
        with st.spinner("Fetching transcript..."):
            try:
                transcript = get_transcript(url)
                st.session_state.transcript = transcript
            except Exception as e:
                st.error(f"Couldn't load transcript: {e}")
                st.session_state.transcript = None

        if st.session_state.transcript:
            with st.spinner("Building vector index..."):
                vectorstore = build_vectorstore(st.session_state.transcript)
                st.session_state.qa_chain = build_qa_chain(vectorstore)
            st.success(f"Video loaded — {len(st.session_state.transcript)} characters of transcript indexed.")

# --- Step 2: Summarize ---
if st.session_state.transcript:
    st.divider()
    st.subheader("Summary")
    if st.button("Generate Summary"):
        with st.spinner("Summarizing with Claude..."):
            summary = summarize_transcript(st.session_state.transcript)
        st.markdown(summary)

# --- Step 3: Ask questions ---
if st.session_state.qa_chain:
    st.divider()
    st.subheader("Ask a question about this video")
    question = st.text_input("Your question", placeholder="What does the speaker say about...?")

    if st.button("Ask"):
        if not question:
            st.warning("Type a question first.")
        else:
            with st.spinner("Thinking..."):
                answer = st.session_state.qa_chain.invoke(question)
            st.markdown(f"**Answer:** {answer}")