"""Ollama embeddings and ChromaDB vector store for RAG."""

import hashlib
import logging
import shutil

import chromadb
import httpx

from app.core.config import settings
from app.services.vnd_service import RAG_CHUNKS_PATH

logger = logging.getLogger(__name__)

CHROMA_DIR = RAG_CHUNKS_PATH.parent / "chroma"
COLLECTION_NAME = "vnd_chunks"


class EmbeddingService:
    @staticmethod
    def is_available() -> bool:
        if not settings.llm_enabled:
            return False
        try:
            with httpx.Client(timeout=3.0) as client:
                response = client.get(f"{settings.ollama_base_url}/api/tags")
                if response.status_code != 200:
                    return False
                models = [
                    item.get("name", "")
                    for item in response.json().get("models", [])
                    if item.get("name")
                ]
                target = settings.embedding_model
                return any(
                    model == target or model.startswith(f"{target}:")
                    for model in models
                )
        except httpx.HTTPError:
            return False

    @staticmethod
    def embed_text(text: str) -> list[float] | None:
        payload = {
            "model": settings.embedding_model,
            "prompt": text,
        }
        try:
            with httpx.Client(timeout=8.0) as client:
                response = client.post(
                    f"{settings.ollama_base_url}/api/embeddings",
                    json=payload,
                )
                response.raise_for_status()
                embedding = response.json().get("embedding")
                if isinstance(embedding, list) and embedding:
                    return embedding
        except httpx.HTTPError as error:
            logger.warning("Embedding request failed: %s", error)
        return None

    @staticmethod
    def _chunk_id(chunk: dict, index: int) -> str:
        raw = f"{chunk.get('document_code', '')}:{chunk.get('section', '')}:{chunk.get('text', '')[:120]}:{index}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def get_client() -> chromadb.PersistentClient:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(CHROMA_DIR))

    @staticmethod
    def get_collection():
        client = EmbeddingService.get_client()
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def rebuild_index(chunks: list[dict]) -> int:
        if CHROMA_DIR.exists():
            shutil.rmtree(CHROMA_DIR, ignore_errors=True)

        if not chunks or not EmbeddingService.is_available():
            return 0

        collection = EmbeddingService.get_collection()
        ids: list[str] = []
        embeddings: list[list[float]] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        consecutive_failures = 0
        max_consecutive_failures = 5

        for index, chunk in enumerate(chunks):
            text = chunk.get("text", "").strip()
            if not text:
                continue
            embedding = EmbeddingService.embed_text(text)
            if not embedding:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    logger.warning(
                        "Stopping Chroma rebuild after %s consecutive embedding failures",
                        max_consecutive_failures,
                    )
                    break
                continue
            consecutive_failures = 0
            ids.append(EmbeddingService._chunk_id(chunk, index))
            embeddings.append(embedding)
            documents.append(text)
            metadatas.append(
                {
                    "document_code": chunk.get("document_code", ""),
                    "source": chunk.get("source", ""),
                    "section": chunk.get("section", ""),
                }
            )

        if not ids:
            return 0

        batch_size = 32
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            collection.add(
                ids=ids[start:end],
                embeddings=embeddings[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

        return len(ids)

    @staticmethod
    def search(query: str, limit: int | None = None) -> list[dict]:
        if not EmbeddingService.is_available():
            return []

        query_embedding = EmbeddingService.embed_text(query)
        if not query_embedding:
            return []

        collection = EmbeddingService.get_collection()
        if collection.count() == 0:
            return []

        top_k = limit or settings.rag_search_limit
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        matches: list[dict] = []
        for document, metadata, distance in zip(documents, metadatas, distances, strict=False):
            score = max(0.0, 1.0 - float(distance))
            if score < settings.rag_min_score:
                continue
            matches.append(
                {
                    "document_code": metadata.get("document_code", ""),
                    "source": metadata.get("source", ""),
                    "section": metadata.get("section", ""),
                    "text": document,
                    "score": score,
                }
            )

        return matches

    @staticmethod
    def chroma_ready() -> bool:
        try:
            collection = EmbeddingService.get_collection()
            return collection.count() > 0
        except Exception:
            return False

    @staticmethod
    def chroma_count() -> int:
        try:
            return EmbeddingService.get_collection().count()
        except Exception:
            return 0
