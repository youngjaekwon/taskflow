# SvelteKit Web Application
# Build context: repository root (.)
# Usage: docker compose up web

FROM node:22-alpine

RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

WORKDIR /app

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --frozen-lockfile --filter @taskflow/web

COPY apps/web/ apps/web/

WORKDIR /app/apps/web

EXPOSE 5173

CMD ["pnpm", "dev", "--host"]
