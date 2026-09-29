# WhyRank

WhyRank is an explainable information-retrieval project with a React/Vite frontend and a FastAPI backend. It ranks CORA machine-learning papers with keyword, MiniLM semantic, PageRank authority, and freshness signals.

## Repository layout

- `frontend/` — React and Vite user interface
- `backend/` — FastAPI API, ranking engine, and tests
- `data/` — versioned seed corpus and judged evaluation queries
- `evaluation/` — ranking evaluation harness

## Environment configuration

Copy `backend/.env.example` to `backend/.env` and set the values required for your local environment. `backend/.env` is intentionally ignored by Git.

```bash
cd backend
cp .env.example .env
```

Required configuration:

- `HF_TOKEN` — Hugging Face access token, when needed to download or access models.
- `API_WRITE_TOKEN` — secret used to protect document-write and reindex API routes. Generate one with `openssl rand -hex 32`.
- `CORS_ALLOWED_ORIGINS` — comma-separated allowed frontend origins.
- `API_RATE_LIMIT_PER_MINUTE` — API request limit per client IP.

Never add real secrets to this repository. Use deployment-platform secrets for hosted environments.
