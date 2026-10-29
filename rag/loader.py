from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document


def load_and_chunk_guidelines(
    file_path: str = "guideline.txt",
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Load the guideline file and split it into semantically meaningful chunks."""
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        keep_separator=True,
    )
    chunks = splitter.split_documents(documents)
    return chunks
