## Context

SvelteKit 2 + Svelte 5 기반 프론트엔드에서 backend-graphene의 API를 소비하여 P0 핵심 기능을 구현한다. 백엔드는 인증에 REST API, 데이터 조작에 GraphQL API를 사용하는 하이브리드 구조이다.

**제약 사항:**
- 별도 GraphQL 클라이언트 라이브러리 없음 (SvelteKit fetch 직접 사용)
- Svelte 5 Runes 문법 전면 사용 (레거시 문법 금지)
- 서버 load 우선 패턴 (`+page.server.ts`)
- Tailwind CSS v4 스타일링

## Goals / Non-Goals

- **Goals:**
  - P0 기능 명세의 모든 항목을 웹 UI로 구현
  - 서버 사이드 렌더링(SSR) 호환
  - 프로그레시브 인핸스먼트 (JavaScript 비활성화 시에도 기본 동작)
  - 안전한 JWT 토큰 관리 (httpOnly 쿠키)

- **Non-Goals:**
  - 실시간 기능 (P2 범위)
  - 모바일 최적화 (반응형 기본 지원은 하되 모바일 전용 UI는 제외)
  - 오프라인 지원
  - backend-strawberry 연동 (현재는 graphene만)

## Decisions

### 1. JWT 토큰 관리: httpOnly 쿠키 방식

- **결정:** SvelteKit 서버가 JWT 토큰을 httpOnly 쿠키로 관리
- **근거:** XSS 공격으로부터 토큰 보호, SvelteKit SSR과 자연스럽게 통합
- **대안:** localStorage → XSS 취약, 서버 사이드 렌더링 불가

**흐름:**
1. 로그인 성공 → 서버 액션이 백엔드에서 토큰 수신 → httpOnly 쿠키 설정
2. 매 요청 → `hooks.server.ts`에서 쿠키 읽기 → `event.locals`에 토큰/사용자 정보 저장
3. GraphQL 요청 → `graphqlRequest`에 토큰 전달 → Authorization 헤더 추가
4. 토큰 만료 → 서버 훅에서 자동 리프레시 → 새 쿠키 설정
5. 로그아웃 → 서버 액션이 백엔드에 로그아웃 요청 → 쿠키 삭제

### 2. 라우트 구조: 라우트 그룹 기반 인증 분리

- **결정:** `(auth)`와 `(app)` 라우트 그룹으로 인증 여부에 따른 레이아웃 분리
- **근거:** SvelteKit 라우트 그룹은 URL에 영향 없이 레이아웃을 공유할 수 있어, 인증된 앱 영역과 비인증 페이지를 깔끔하게 분리

```
src/routes/
├── +layout.svelte                          # 루트 레이아웃
├── +layout.server.ts                       # 루트 load (사용자 정보)
├── +page.svelte                            # 랜딩 페이지
├── (auth)/                                 # 비인증 라우트 그룹
│   ├── +layout.svelte                      # 인증 페이지 레이아웃 (센터 정렬 등)
│   ├── login/+page.svelte, +page.server.ts
│   ├── register/+page.svelte, +page.server.ts
│   ├── verify-email/+page.svelte, +page.server.ts
│   ├── forgot-password/+page.svelte, +page.server.ts
│   └── reset-password/+page.svelte, +page.server.ts
├── (app)/                                  # 인증 필수 라우트 그룹
│   ├── +layout.svelte                      # 앱 레이아웃 (네비게이션 등)
│   ├── +layout.server.ts                   # 인증 검증 + 사용자 데이터 로드
│   ├── profile/+page.svelte, +page.server.ts
│   ├── orgs/
│   │   ├── +page.svelte, +page.server.ts           # 내 Organization 목록
│   │   ├── new/+page.svelte, +page.server.ts        # Organization 생성
│   │   └── [orgId]/
│   │       ├── +layout.svelte, +layout.server.ts    # Org 레이아웃 (사이드바)
│   │       ├── +page.svelte, +page.server.ts        # Org 상세/설정
│   │       ├── members/+page.svelte, +page.server.ts
│   │       └── projects/
│   │           ├── +page.svelte, +page.server.ts
│   │           ├── new/+page.svelte, +page.server.ts
│   │           └── [projectId]/
│   │               ├── +layout.svelte, +layout.server.ts
│   │               ├── +page.svelte, +page.server.ts
│   │               ├── members/+page.svelte, +page.server.ts
│   │               └── boards/
│   │                   └── [boardId]/
│   │                       └── +page.svelte, +page.server.ts  # 칸반 보드
```

### 3. 데이터 로딩: 서버 load + Form Actions

- **결정:** 모든 GraphQL 쿼리는 `+page.server.ts`의 load 함수에서 실행, 뮤테이션은 SvelteKit Form Actions로 처리
- **근거:** 시크릿 보호, SSR 최적화, CSRF 자동 보호, 프로그레시브 인핸스먼트

### 4. API 통합: REST (인증) + GraphQL (데이터)

- **결정:** 인증은 REST API, 데이터 조작은 GraphQL API 사용
- **근거:** backend-graphene이 인증을 REST 엔드포인트로 제공하고, 나머지를 GraphQL로 제공하는 구조를 따름

**구현:**
- `$lib/server/auth.ts`: REST 인증 API 호출 유틸리티 (register, login, logout, token refresh 등)
- `$lib/server/graphql.ts`: 기존 GraphQL 요청 유틸리티 확장 (Authorization 헤더 추가)

### 5. 상태 관리: 서버 데이터 중심

- **결정:** 글로벌 클라이언트 상태 최소화, 대부분의 상태는 서버 load에서 제공
- **근거:** SvelteKit의 서버 load + invalidation 패턴으로 충분, 추가 상태 라이브러리 불필요

**패턴:**
- 페이지 데이터: `+page.server.ts` load → `data` prop
- 레이아웃 공유 데이터: `+layout.server.ts` load (사용자 정보, Organization 정보)
- 로컬 UI 상태: `$state` (모달 열림, 폼 입력값 등)
- 데이터 갱신: Form Action 후 자동 revalidation 또는 `invalidate()`

### 6. 컴포넌트 구조

- **결정:** 기능별 페이지 컴포넌트 + 공유 UI 컴포넌트 분리

```
$lib/components/
├── ui/              # 범용 UI 컴포넌트
│   ├── Button.svelte
│   ├── Input.svelte
│   ├── Modal.svelte
│   ├── Select.svelte
│   ├── Badge.svelte
│   ├── Avatar.svelte
│   ├── Pagination.svelte
│   └── DropdownMenu.svelte
├── board/           # Board 관련 컴포넌트
│   ├── KanbanBoard.svelte
│   ├── TaskGroup.svelte
│   └── TaskCard.svelte
└── layout/          # 레이아웃 컴포넌트
    ├── Navbar.svelte
    ├── Sidebar.svelte
    └── PageHeader.svelte
```

### 7. 인가 구현 전략

- **결정:** 3단계 인가 체크
  1. **라우트 보호:** `(app)/+layout.server.ts`에서 토큰 없으면 로그인으로 리다이렉트
  2. **리소스 접근:** 각 `+page.server.ts`의 load에서 GraphQL 에러(권한 부족)를 SvelteKit error로 변환
  3. **UI 제어:** 사용자 역할 정보를 레이아웃 load에서 제공, 컴포넌트에서 역할 기반 렌더링

## Risks / Trade-offs

- **REST + GraphQL 혼합:** 두 가지 API 패턴을 동시에 사용하므로 유틸리티가 분리됨 → 명확한 디렉터리 구분으로 완화
- **httpOnly 쿠키 토큰:** 서버에서만 토큰 접근 가능하므로, 클라이언트에서 직접 API 호출 불가 → 모든 뮤테이션은 Form Actions로 처리하여 해결
- **딥 네스팅 라우트:** `/orgs/[orgId]/projects/[projectId]/boards/[boardId]`는 5단계 깊이 → SvelteKit 레이아웃 상속으로 각 단계에서 필요한 데이터만 로드

## Open Questions

- (없음 — 백엔드 API 스펙이 이미 확정되어 있으므로 프론트엔드 구현에 모호한 점 없음)
