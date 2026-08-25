from pathlib import Path
import yaml

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.config import KNOWLEDGE_BASE_DIR, VECTOR_DB_DIR


def parse_markdown_file(path: Path):
    """
    Read a Markdown file containing YAML front matter.

    Returns:
        metadata: dictionary containing document metadata
        content: Markdown content without front matter
    """

    text = path.read_text(encoding="utf-8")

    metadata = {}
    content = text

    if text.startswith("---"):
        parts = text.split("---", 2)

        if len(parts) == 3:
            raw_metadata = yaml.safe_load(parts[1]) or {}

            # Convert YAML date objects and other values
            # into simple values that Chroma can safely store.
            metadata = {
                key: str(value)
                for key, value in raw_metadata.items()
            }

            content = parts[2].strip()

    return metadata, content


def load_documents():
    """
    Load all Markdown knowledge-base documents.
    """

    documents = []

    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        metadata, content = parse_markdown_file(path)

        documents.append(
            Document(
                page_content=content,
                metadata={
                    **metadata,
                    "source_file": path.name
                }
            )
        )

    return documents


def build_index():
    """
    Build the local Chroma vector database.
    """

    documents = load_documents()

    print(f"Loaded {len(documents)} documents.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

    print("Building Chroma index...")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(VECTOR_DB_DIR),
        collection_name="aster_row_kb"
    )

    print(f"Indexed {len(chunks)} chunks successfully.")
    print(f"Vector database location: {VECTOR_DB_DIR}")


if __name__ == "__main__":
    build_index()