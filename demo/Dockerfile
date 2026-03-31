FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY knowledge ./knowledge

RUN pip install --no-cache-dir uv \
    && uv pip install --system .

COPY .env ./.env

CMD ["tail", "-f", "/dev/null"]
