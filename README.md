# BE-TECH News Alert System

News monitoring & alerting system built for Dec 8 demo.

## Features

- Multi-source ingestion (RSS + NewsAPI)
- AI-powered topic classification (offline HuggingFace)
- De-duplication & persistence (PostgreSQL)
- Background processing (Redis + RQ)
- Email alerts with HTML templates
- Live dashboard (Streamlit)
- Fully Dockerized

## Quick start

```bash
cp .env.example .env
docker compose up --build
```
