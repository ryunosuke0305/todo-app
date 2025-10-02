# syntax=docker/dockerfile:1.4

# Frontend build stage
FROM node:18 AS frontend-build
WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend runtime stage
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-build /workspace/frontend/dist ./frontend_dist/

ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app/backend

EXPOSE 5000
CMD ["python", "run.py"]
