# Project Context

## Purpose
GraphQL 기반 태스크 관리 연습 프로젝트. 두 가지 Django GraphQL 라이브러리(Graphene, Strawberry)를 SvelteKit 프론트엔드와 함께 비교 학습한다.

## Tech Stack
- **모노레포**: Turborepo + pnpm 10.4.1
- **프론트엔드**: SvelteKit (Node 22)
- **백엔드**: Django + Graphene (Python 3.13), Django + Strawberry (Python 3.13)
- **컨테이너**: Docker Compose

## Apps
| 앱 | 패키지명 | 포트 | 설명 |
|----|----------|------|------|
| `apps/backend-graphene` | `@taskflow/backend-graphene` | 8001 | Django + Graphene GraphQL 백엔드 |
| `apps/backend-strawberry` | `@taskflow/backend-strawberry` | 8002 | Django + Strawberry GraphQL 백엔드 |
| `apps/web` | `@taskflow/web` | 5173 | SvelteKit 프론트엔드 |

## Spec Naming Convention
모노레포 내 앱별 스펙을 구분하기 위해 `{앱}-{도메인}` 네이밍을 사용한다:
- `graphene-tasks`, `graphene-auth` — backend-graphene 관련 스펙
- `strawberry-tasks`, `strawberry-auth` — backend-strawberry 관련 스펙
- `web-dashboard`, `web-auth` — web 관련 스펙
- `shared-schema` — 앱 간 공유 스펙 (GraphQL 스키마 등)

변경(change) 네이밍: `{동사}-{앱}-{도메인}` (예: `add-graphene-tasks`, `update-web-auth`)

## Project Conventions

### Code Style
- Python: PEP 8, Django 컨벤션
- TypeScript/Svelte: Prettier, ESLint
- 답변 및 문서는 한국어로 작성

### Architecture Patterns
- 하이브리드 모노레포: Node.js Turborepo가 오케스트레이터, Python Django 백엔드는 `package.json` 래퍼로 Turbo 파이프라인에 통합
- 두 백엔드는 동일한 태스크 관리 GraphQL API를 각각 다른 라이브러리로 구현
- 프론트엔드는 두 백엔드 중 하나에 연결하여 동작

### Testing Strategy
- 각 앱별 독립 테스트 (`pnpm test --filter @taskflow/<앱>`)
- 전체 테스트: `pnpm test`

### Git Workflow
- 메인 브랜치: `main`
- Conventional Commits 형식 사용

## Domain Context
태스크 관리 도메인: Task CRUD, 상태 관리 (TODO/IN_PROGRESS/IN_REVIEW/DONE), 우선순위, 라벨

## Important Constraints
- 현재 보일러플레이트 단계 — 각 앱의 스크립트와 Dockerfile은 placeholder
- 두 백엔드는 동일한 GraphQL 스키마를 구현해야 비교가 유의미함

## External Dependencies
- Docker Compose: 로컬 개발 환경 컨테이너 오케스트레이션
