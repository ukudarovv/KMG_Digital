"""Index knowledge documents from Docs into RAG chunk store."""

from app.services.knowledge_index_service import KnowledgeIndexService


def index_vnd_documents() -> dict:
    return KnowledgeIndexService.index_all_documents()


if __name__ == "__main__":
    result = index_vnd_documents()
    print(
        "Indexed knowledge base:",
        f"{result.get('chunks_count', 0)} chunks,",
        f"{len(result.get('indexed_documents', []))} documents,",
        f"Chroma: {result.get('chroma_count', 0)} vectors.",
    )
