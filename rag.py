from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import chromadb
import httpx
from chromadb.api.models.Collection import Collection
from sentence_transformers import SentenceTransformer

from rag_config import RAGConfig, config


@dataclass
class RetrievedChunk:
    text: str
    similarity: float


class RAGPipeline:
    def __init__(self, rag_config: RAGConfig = config) -> None:
        self.config = rag_config
        self._embedder: SentenceTransformer | None = None
        self._collection: Collection | None = None
        self._client: chromadb.ClientAPI | None = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            raise RuntimeError("RAG pipeline is not indexed yet. Call index() first.")
        return self._embedder

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            raise RuntimeError("RAG pipeline is not indexed yet. Call index() first.")
        return self._collection

    def index(self) -> None:
        """Load, chunk, embed, and store the knowledge base in memory."""
        path = Path(self.config.knowledge_base_path)
        raw = path.read_text(encoding="utf-8")
        chunks = self._chunk_knowledge_base(raw)
        if not chunks:
            raise ValueError(f"No chunks found in {path}")

        self._embedder = SentenceTransformer(self.config.embedding_model)
        embeddings = self._embedder.encode(chunks, normalize_embeddings=True).tolist()

        self._client = chromadb.EphemeralClient()
        self._collection = self._client.create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        self._collection.add(
            ids=[f"chunk-{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=embeddings,
        )

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        """Return top_k chunks that meet the similarity threshold."""
        query_embedding = self.embedder.encode(
            [query], normalize_embeddings=True
        ).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=self.config.top_k,
            include=["documents", "distances"],
        )

        documents = (results.get("documents") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for doc, distance in zip(documents, distances):
            # Chroma cosine space uses distance = 1 - cosine_similarity
            similarity = 1.0 - float(distance)
            if similarity >= self.config.similarity_threshold:
                retrieved.append(RetrievedChunk(text=doc, similarity=similarity))
        return retrieved

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> str:
        """Call Ollama with retrieved context and shared generation settings."""
        if chunks:
            context = "\n\n".join(
                f"[similarity={c.similarity:.3f}] {c.text}" for c in chunks
            )
            system = (
                "You are a helpful assistant for BEON.tech. "
                "Answer the user's question using only the provided knowledge base context. "
                "If the context is insufficient, say you don't have enough information."
            )
            user = f"Context:\n{context}\n\nQuestion: {question}"
        else:
            system = (
                "You are a helpful assistant for BEON.tech. "
                "No relevant knowledge base context was found for this question. "
                "Politely say you don't have enough information to answer."
            )
            user = f"Question: {question}"

        payload = {
            "model": self.config.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "presence_penalty": self.config.presence_penalty,
            },
        }

        url = f"{self.config.ollama_base_url.rstrip('/')}/api/chat"
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["message"]["content"]

    def answer(self, question: str) -> tuple[str, list[RetrievedChunk]]:
        chunks = self.retrieve(question)
        return self.generate(question, chunks), chunks

    @staticmethod
    def _chunk_knowledge_base(raw: str) -> list[str]:
        """Split quoted paragraph blocks into individual chunks."""
        matches = re.findall(r'"([^"]+)"', raw, flags=re.DOTALL)
        chunks = [" ".join(m.split()) for m in matches]
        if chunks:
            return chunks
        # Fallback: non-empty lines joined into paragraphs
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        return [" ".join(p.split()) for p in paragraphs]


pipeline = RAGPipeline()
