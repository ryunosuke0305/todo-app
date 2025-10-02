FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p /app/data
ENV FLASK_APP=run.py \
    TODO_DB_PATH=/app/data/todo.sqlite3
EXPOSE 5000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
