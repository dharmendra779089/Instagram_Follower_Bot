FROM python:3.10-slim

# Install system dependencies, Chromium browser and ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Ensure /dev/shm is large enough for Chromium (default 64MB causes crashes)
RUN mkdir -p /dev/shm && chmod 1777 /dev/shm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "2", "--timeout", "120", "app:app"]
