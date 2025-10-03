# syntax=docker/dockerfile:1.4

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

COPY backend/ ./backend/

RUN mkdir -p /app/backend/data

ENV PATH="/opt/venv/bin:$PATH" \
    TODO_DB_PATH=/app/backend/data/todo.sqlite3
WORKDIR /app/backend

EXPOSE 5000
CMD ["python", "run.py"]
