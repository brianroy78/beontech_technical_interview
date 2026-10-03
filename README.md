# BEON.tech Technical Interview

Minimal Python API with a ready-to-use POST endpoint for the live coding exercise.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Server: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Endpoints

| Method | Path           | Description              |
|--------|----------------|--------------------------|
| GET    | `/health`      | Health check             |
| POST   | `/api/process` | Accepts `{ "message": "..." }` |

### Example (PowerShell)

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/process `
  -ContentType "application/json" `
  -Body '{"message":"hello"}'
```

Or use the interactive docs at `/docs`.