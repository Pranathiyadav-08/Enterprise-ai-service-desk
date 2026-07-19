# Deployment guide

This guide describes a local deployment of Enterprise AI Service Desk. The frontend is a static site and the backend is an ASGI application.

## 1. Install prerequisites

- Python 3.10 or newer
- Ollama

## 2. Configure the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optionally create `backend/.env` to override the defaults:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

## 3. Start the model service

In a separate terminal:

```powershell
ollama serve
ollama pull llama3.2
```

## 4. Start the API

From `backend/` with the virtual environment active:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

Verify it is available at `http://localhost:8000/health`.

## 5. Serve the frontend

From the repository root:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://localhost:5500`. The current frontend configuration uses `http://localhost:8000` as its API base URL.

## Operational notes

- Keep `.env`, generated FAISS indexes, and confidential PDFs outside version control.
- For an internet-facing deployment, restrict CORS origins, place the API behind TLS, and run the application through an appropriate process manager or container platform.
- Store persistent knowledge-base documents and vector indexes on durable storage.
