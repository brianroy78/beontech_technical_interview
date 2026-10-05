# BEON.tech Technical Interview

Minimal FastAPI RAG service: embeds `knowledge_base.txt` into an in-memory Chroma store and answers via local Ollama.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Requires a local Ollama instance with model `gemma4:12b`.

## Run

```bash
python main.py
```

Server: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Configuration

Shared settings live in `rag_config.py` (`RAGConfig`): model, temperature, top_p, presence_penalty, embedding model, top_k, similarity_threshold, Ollama URL, and knowledge base path.

## Endpoints

| Method | Path           | Description                                      |
|--------|----------------|--------------------------------------------------|
| GET    | `/health`      | Health check                                     |
| POST   | `/api/process` | RAG Q&A: `{ "message": "..." }` → answer + sources |

### Example (PowerShell)

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/process `
  -ContentType "application/json" `
  -Body '{"message":"What is BEON.tech mission?"}'
```

Or use the interactive docs at `/docs`.
