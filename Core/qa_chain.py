# Core/qa_chain.py

import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

load_dotenv()  # reads ANTHROPIC_API_KEY from your .env file

QA_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant answering questions about a YouTube video,
based only on its transcript.

Use ONLY the context below to answer the question. If the answer isn't
in the context, say you don't know — don't make anything up.

Context:
{context}

Question: {question}

Answer:"""
)


def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_qa_chain(vectorstore, model: str = "claude-sonnet-4-6"):
    """
    Wires a FAISS retriever to Claude via an LCEL pipeline:
    question -> retrieve relevant chunks -> stuff into prompt -> Claude -> text answer
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatAnthropic(model=model, temperature=0)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | QA_PROMPT
        | llm
        | StrOutputParser()
    )
    return chain


if __name__ == "__main__":
    from loader import get_transcript
    from vectorstore import build_vectorstore

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript = get_transcript(test_url)
    vs = build_vectorstore(transcript)

    chain = build_qa_chain(vs)
    question = "What is the main message of this video?"
    answer = chain.invoke(question)

    print(f"Q: {question}\nA: {answer}")