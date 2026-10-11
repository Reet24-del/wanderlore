FROM python:3.12-slim
WORKDIR /app
COPY deploy/render/requirements.txt ./requirements-render.txt
RUN pip install --no-cache-dir -r requirements-render.txt
COPY app ./app
COPY web ./web
COPY deploy/render ./deploy/render
COPY docs/lucknow-places.geojson ./deploy/render/lucknow-places.geojson
ENV WANDERLORE_DATA=/tmp/wanderlore WANDERLORE_HOSTED=1 WANDERLORE_TEMPORARY_STORAGE=1 WANDERLORE_NARRATOR=google WANDERLORE_MODEL=gemma-4-26b-a4b-it PYTHONUNBUFFERED=1
CMD ["bash", "deploy/render/start.sh"]
