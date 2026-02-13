<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

GraphQL 기반 태스크 관리 연습 프로젝트. 두 가지 Django GraphQL 라이브러리(Graphene, Strawberry)를 SvelteKit 프론트엔드와 함께 비교 학습한다.

## 아키텍처

하이브리드 모노레포 구조를 사용한다. Node.js 기반 Turborepo가 모노레포 오케스트레이터 역할을 하며, Python Django 백엔드들은 각 앱 디렉터리의 `package.json` 래퍼를 통해 Turbo 파이프라인에 통합된다.

두 백엔드(`backend-graphene`, `backend-strawberry`)는 동일한 태스크 관리 GraphQL API를 각각 Graphene과 Strawberry로 구현한다. 이를 통해 두 라이브러리의 DX, 성능, 타입 시스템을 직접 비교할 수 있다. 프론트엔드(`web`)는 두 백엔드 중 하나에 연결하여 동작한다.

## 기술 스택

| 영역       | 기술                                                 |
| ---------- | ---------------------------------------------------- |
| 모노레포   | Turborepo + pnpm 10.4.1                              |
| 프론트엔드 | SvelteKit (Node 22)                                  |
| 백엔드     | Django + Graphene, Django + Strawberry (Python 3.13) |
| 컨테이너   | Docker Compose                                       |

## 주요 명령어

```bash
# Turbo 태스크 (루트에서 실행)
pnpm dev          # 모든 앱 dev 서버 실행
pnpm build        # 모든 앱 빌드
pnpm lint         # 모든 앱 린트
pnpm test         # 모든 앱 테스트

# 단일 앱 실행
pnpm dev --filter @taskflow/web
pnpm dev --filter @taskflow/backend-graphene
pnpm dev --filter @taskflow/backend-strawberry

# Docker
pnpm docker:up    # docker compose up
pnpm docker:down  # docker compose down
pnpm docker:build # docker compose build
```

## 포트 매핑

| 서비스             | 호스트 포트 | 컨테이너 포트 |
| ------------------ | ----------- | ------------- |
| web (SvelteKit)    | 5173        | 5173          |
| backend-graphene   | 8001        | 8000          |
| backend-strawberry | 8002        | 8000          |

## 개발 컨벤션

- **Python 패키지 매니저**: uv
- **Python 린터 & 포매터**: ruff
- **`rm` 사용 시**: 반드시 `-f` 플래그를 붙여야 한다 (예: `rm -f`, `rm -rf`)
- **패키지 네이밍**: `@taskflow/<패키지명>` (예: `@taskflow/web`)
- **워크스페이스**: `apps/*`, `packages/*`
- **Dockerfile 위치**: 각 앱 디렉터리 내부 (`apps/<앱>/Dockerfile`), 빌드 컨텍스트는 레포 루트
- **현재 상태**: 보일러플레이트 단계 — 각 앱의 스크립트와 Dockerfile은 placeholder
