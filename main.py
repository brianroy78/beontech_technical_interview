from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag import pipeline
from rag_config import config


class ProcessRequest(BaseModel):
    message: str = Field(..., min_length=1)


class SourceChunk(BaseModel):
    text: str
    similarity: float


class ProcessResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    pipeline.index()
    yield


app = FastAPI(title="Interview API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    try:
        answer, chunks = pipeline.answer(request.message)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama request failed ({config.model}): {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ProcessResponse(
        answer=answer,
        sources=[
            SourceChunk(text=c.text, similarity=c.similarity) for c in chunks
        ],
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
