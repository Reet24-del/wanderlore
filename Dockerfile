FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libsndfile1 espeak-ng curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt requirements-sponsors.txt ./
RUN pip install --no-cache-dir -r requirements-sponsors.txt
COPY app ./app
COPY web ./web
ENV WANDERLORE_DATA=/app/data PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8766", "--no-proxy-headers"]
