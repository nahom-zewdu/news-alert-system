FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-install-project

EXPOSE 8000 8501

ENV PYTHONPATH=/app

CMD ["sh", "-c", \
"PYTHONPATH=/app uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
 PYTHONPATH=/app uv run streamlit run /app/app/ui/dashboard.py --server.port=8501"]
