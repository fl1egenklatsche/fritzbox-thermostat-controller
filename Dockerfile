FROM python:3.11-slim

WORKDIR /app

# Install system deps for fritzconnection optional features and sqlite
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev build-essential sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=9999

EXPOSE 9999

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999", "--proxy-headers"]
