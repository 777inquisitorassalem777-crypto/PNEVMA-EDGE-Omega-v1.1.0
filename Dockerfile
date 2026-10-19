
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
RUN pip install --no-cache-dir '.[api,postgres,embeddings]'
COPY . .
RUN mkdir -p /app/results /app/data
EXPOSE 8000
CMD ["uvicorn","symbio_core.api:app","--host","0.0.0.0","--port","8000"]
