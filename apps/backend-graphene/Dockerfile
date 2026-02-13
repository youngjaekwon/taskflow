# Django + Graphene Backend
# Build context: repository root (.)
# Usage: docker compose up backend-graphene

FROM python:3.13-slim

WORKDIR /app/apps/backend-graphene

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY apps/backend-graphene/pyproject.toml apps/backend-graphene/uv.lock ./
RUN uv sync --frozen --no-dev

COPY apps/backend-graphene/ ./

EXPOSE 8000

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
