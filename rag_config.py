from dataclasses import dataclass


@dataclass
class RAGConfig:
    """Shared tunable settings for the RAG pipeline."""

    model: str = "gemma4:12b"
    temperature: float = 0.2
    top_p: float = 0.9
    presence_penalty: float = 0.0
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k: int = 1
    similarity_threshold: float = 0.55
    ollama_base_url: str = "http://localhost:11434"
    knowledge_base_path: str = "knowledge_base.txt"


config = RAGConfig()
