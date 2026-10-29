import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document
from rag.loader import load_and_chunk_guidelines


class Reranker:
    """Cross-encoder reranker for improving retrieval relevance."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, documents: list[Document], top_k: int = 5) -> list[Document]:
        if not documents:
            return []
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)
        scored = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]


class GuidelineRetriever:
    """RAG retriever with FAISS vector store and cross-encoder reranking."""

    def __init__(self, guidelines_path: str = "guideline.txt", api_key: str = ""):
        self.guidelines_path = guidelines_path
        self.api_key = api_key
        self.vectorstore = None
        self.reranker = None
        self._initialized = False

    def initialize(self):
        """Build the vector store and reranker (called once)."""
        if self._initialized:
            return

        chunks = load_and_chunk_guidelines(self.guidelines_path)

        embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.vectorstore = FAISS.from_documents(chunks, embeddings)
        self.reranker = Reranker()
        self._initialized = True

    def retrieve(self, query: str, top_k: int = 5, initial_k: int = 15) -> str:
        """Retrieve relevant guideline sections using similarity search + reranking."""
        self.initialize()

        # Stage 1: broad retrieval from FAISS
        candidates = self.vectorstore.similarity_search(query, k=initial_k)

        # Stage 2: rerank with cross-encoder
        reranked = self.reranker.rerank(query, candidates, top_k=top_k)

        return "\n\n---\n\n".join(doc.page_content for doc in reranked)

    def retrieve_all(self) -> str:
        """Return the full guideline document."""
        with open(self.guidelines_path, "r", encoding="utf-8") as f:
            return f.read()


# ── Singleton accessors ───────────────────────────────────────────
_retriever_cache: dict[str, GuidelineRetriever] = {}


def get_retriever(guidelines_path: str | None = None) -> GuidelineRetriever:
    """
    Return (and lazily create) a GuidelineRetriever for the given file.
    Each guideline file gets its own FAISS index and reranker.
    If no path given, returns the default (spec-driven chat) retriever.
    """
    from config.settings import get_settings
    settings = get_settings()

    path = guidelines_path or settings.GUIDELINES_PATH

    if path not in _retriever_cache:
        _retriever_cache[path] = GuidelineRetriever(
            guidelines_path=path,
            api_key=settings.OPENAI_API_KEY,
        )
    return _retriever_cache[path]


def get_developer_retriever() -> GuidelineRetriever:
    """Return the Developer Agent's guideline retriever."""
    return get_retriever("guidelines/developer_guidelines.txt")


def get_tester_retriever() -> GuidelineRetriever:
    """Return the Tester Agent's guideline retriever."""
    return get_retriever("guidelines/tester_guidelines.txt")


def get_devops_retriever() -> GuidelineRetriever:
    """Return the DevOps Agent's guideline retriever."""
    return get_retriever("guidelines/devops_guidelines.txt")


def get_ba_retriever() -> GuidelineRetriever:
    """Return the BA Agent's guideline retriever."""
    return get_retriever("guidelines/ba_guidelines.txt")
