## 1. 인프라 & 기반 구축

- [ ] 1.1 TypeScript 타입 정의 — GraphQL 응답 타입, 공통 인터페이스 (`$lib/types/`)
- [ ] 1.2 REST 인증 API 유틸리티 생성 (`$lib/server/auth.ts`)
- [ ] 1.3 GraphQL 유틸리티 확장 — Authorization 헤더 지원 (`$lib/server/graphql.ts`)
- [ ] 1.4 GraphQL 쿼리/뮤테이션/프래그먼트 정의 (`$lib/graphql/`)
- [ ] 1.5 공통 UI 컴포넌트 생성 — Button, Input, Modal, Select, Badge, Avatar, Pagination (`$lib/components/ui/`)
- [ ] 1.6 레이아웃 컴포넌트 생성 — Navbar, Sidebar, PageHeader (`$lib/components/layout/`)
- [ ] 1.7 `App.Locals` 타입 정의 — user, accessToken 필드 추가 (`app.d.ts`)

## 2. 인증 (web-auth)

- [ ] 2.1 서버 훅 구현 — 쿠키에서 토큰 읽기, `event.locals` 설정, 토큰 자동 리프레시 (`hooks.server.ts`)
- [ ] 2.2 `(auth)` 라우트 그룹 레이아웃 — 센터 정렬 인증 페이지 레이아웃
- [ ] 2.3 회원가입 페이지 — 이메일/비밀번호 폼, 유효성 검사, Form Action (`(auth)/register/`)
- [ ] 2.4 로그인 페이지 — 이메일/비밀번호 폼, JWT 쿠키 설정, Form Action (`(auth)/login/`)
- [ ] 2.5 이메일 인증 페이지 — 토큰 검증, 재발송 기능 (`(auth)/verify-email/`)
- [ ] 2.6 비밀번호 초기화 요청 페이지 — 이메일 입력 폼 (`(auth)/forgot-password/`)
- [ ] 2.7 비밀번호 초기화 확인 페이지 — 새 비밀번호 입력 폼 (`(auth)/reset-password/`)
- [ ] 2.8 프로필 페이지 — 프로필 조회/수정, 아바타 업로드/삭제, 비밀번호 변경 (`(app)/profile/`)
- [ ] 2.9 로그아웃 기능 — Form Action, 쿠키 삭제

## 3. 인가 (web-authz)

- [ ] 3.1 `(app)` 라우트 그룹 레이아웃 — 인증 검증, 미인증 시 로그인 리다이렉트 (`(app)/+layout.server.ts`)
- [ ] 3.2 Organization 접근 검증 — `[orgId]` 레이아웃 load에서 멤버십 확인 및 역할 데이터 제공
- [ ] 3.3 Project 접근 검증 — `[projectId]` 레이아웃 load에서 프로젝트 접근 권한 확인
- [ ] 3.4 GraphQL 에러 → SvelteKit 에러 변환 — 권한 부족 시 403, 리소스 미발견 시 404
- [ ] 3.5 역할 기반 UI 조건부 렌더링 — 역할에 따른 버튼/메뉴 표시/숨김

## 4. Organization (web-org)

- [ ] 4.1 내 Organization 목록 페이지 (`(app)/orgs/`)
- [ ] 4.2 Organization 생성 페이지 (`(app)/orgs/new/`)
- [ ] 4.3 Organization 상세/설정 페이지 — 정보 조회, 이름/설명 수정, 삭제 (`(app)/orgs/[orgId]/`)
- [ ] 4.4 `[orgId]` 레이아웃 — Organization 데이터 로드, 사이드 네비게이션
- [ ] 4.5 멤버 관리 페이지 — 멤버 목록, 초대, 역할 변경, 제거 (`(app)/orgs/[orgId]/members/`)

## 5. Project (web-project)

- [ ] 5.1 프로젝트 목록 페이지 (`(app)/orgs/[orgId]/projects/`)
- [ ] 5.2 프로젝트 생성 페이지 (`(app)/orgs/[orgId]/projects/new/`)
- [ ] 5.3 프로젝트 상세/설정 페이지 — 정보 조회/수정/삭제 (`(app)/orgs/[orgId]/projects/[projectId]/`)
- [ ] 5.4 `[projectId]` 레이아웃 — 프로젝트 데이터 로드
- [ ] 5.5 프로젝트 멤버 관리 페이지 — 멤버 목록, 추가, 제거 (`(app)/orgs/[orgId]/projects/[projectId]/members/`)

## 6. Board & TaskGroup (web-board)

- [ ] 6.1 Board 목록/선택 UI — 프로젝트 내 Board 탭 또는 드롭다운
- [ ] 6.2 칸반 보드 페이지 — TaskGroup 컬럼 렌더링 (`(app)/orgs/[orgId]/projects/[projectId]/boards/[boardId]/`)
- [ ] 6.3 Board 생성/수정/삭제 기능 — Form Actions
- [ ] 6.4 TaskGroup 생성/수정/삭제 기능 — Form Actions
- [ ] 6.5 TaskGroup 순서 변경 — 드래그앤드롭 (클라이언트 사이드)

## 7. Task (web-task)

- [ ] 7.1 Task 카드 컴포넌트 — 제목, 상태, 우선순위, 담당자, 기한 표시 (`$lib/components/board/TaskCard.svelte`)
- [ ] 7.2 Task 생성 기능 — 모달 또는 인라인 폼, Form Action
- [ ] 7.3 Task 상세 조회 — 모달 또는 사이드 패널
- [ ] 7.4 Task 수정 기능 — 인라인 편집 또는 상세 뷰에서 수정
- [ ] 7.5 Task 삭제 기능 — 확인 다이얼로그 + Form Action
- [ ] 7.6 Task 상태 변경 — 상태 드롭다운 또는 칸반 드래그
- [ ] 7.7 Task를 다른 TaskGroup으로 이동 — 칸반 보드 드래그앤드롭
- [ ] 7.8 Task 순서 변경 — 같은 TaskGroup 내 드래그앤드롭
- [ ] 7.9 Task 담당자 지정/변경 — 담당자 선택 드롭다운
- [ ] 7.10 Task 목록 필터링 — 상태, 우선순위, 담당자, 기한, 키워드 필터 UI
- [ ] 7.11 Task 목록 페이지네이션 — Pagination 컴포넌트 연동

## 8. 검증 & 마무리

- [ ] 8.1 svelte-check 타입 검사 통과
- [ ] 8.2 Vitest 단위 테스트 — 유틸리티 함수, GraphQL 쿼리 문자열
- [ ] 8.3 Playwright E2E 테스트 — 인증 플로우, 주요 CRUD 플로우
