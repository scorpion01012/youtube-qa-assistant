# Core/vectorstore.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


def split_transcript(text: str, chunk_size: int = 1000, chunk_overlap: int = 150):
    """Splits a long transcript string into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    return [Document(page_content=chunk) for chunk in chunks]


def get_embedding_model():
    """Free, local embedding model — no API cost."""
    return HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")


def build_vectorstore(text: str) -> FAISS:
    """
    Takes the raw transcript text, splits it, embeds it,
    and returns a FAISS vector store ready for retrieval.
    """
    documents = split_transcript(text)
    embeddings = get_embedding_model()
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore


if __name__ == "__main__":
    from loader import get_transcript

    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    transcript = get_transcript(test_url)

    print("Building vector store...")
    vs = build_vectorstore(transcript)
    print(f"Vector store built with {vs.index.ntotal} chunks.")

    # quick similarity search sanity check
    results = vs.similarity_search("what is this video about", k=2)
    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---\n{doc.page_content[:200]}")