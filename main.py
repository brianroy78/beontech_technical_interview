from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Interview API")



@app.post("/api/process")
def process(request) -> str:
    return "Hello, World!"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
