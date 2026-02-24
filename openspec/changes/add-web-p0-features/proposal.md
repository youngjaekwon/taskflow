# Change: Web P0 핵심 기능 구현

## Why

SvelteKit 프론트엔드(`apps/web`)에 P0 핵심 기능을 구현하여, backend-graphene의 GraphQL API와 REST Auth API를 소비하는 완전한 태스크 관리 웹 애플리케이션을 제공한다. 현재 web 앱은 보일러플레이트 상태이며, 인증부터 Task 관리까지 모든 핵심 기능이 부재하다.

## What Changes

- **인증 시스템** (`web-auth`): 로그인, 회원가입, 토큰 관리, 이메일 인증, 비밀번호 변경/초기화, 프로필 조회/수정, 아바타 업로드
- **Organization 관리** (`web-org`): Organization CRUD, 멤버 초대/역할 변경/제거, 소속 Organization 목록
- **Project 관리** (`web-project`): Project CRUD, 멤버 할당/제거, Organization별 프로젝트 목록
- **Board & TaskGroup** (`web-board`): Board CRUD, TaskGroup CRUD, TaskGroup 순서 변경 (드래그앤드롭), 칸반 보드 뷰
- **Task 관리** (`web-task`): Task CRUD, 상태 변경, TaskGroup 간 이동, 순서 변경, 담당자 지정, 복합 필터링, 페이지네이션
- **인가 시스템** (`web-authz`): 보호된 라우트 그룹, 역할 기반 UI 제어, Organization/Project 접근 검증

## Impact

- Affected specs: 신규 6개 — `web-auth`, `web-org`, `web-project`, `web-board`, `web-task`, `web-authz`
- Affected code: `apps/web/src/` 전체 (routes, lib, hooks, types)
- 의존성: backend-graphene의 REST Auth API + GraphQL API
