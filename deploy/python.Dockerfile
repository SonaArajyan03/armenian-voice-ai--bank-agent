FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY bank_support ./bank_support
COPY agent.py token_server.py ./
COPY scripts ./scripts
COPY seeds ./seeds
RUN pip install --no-cache-dir .
CMD ["python", "-V"]
