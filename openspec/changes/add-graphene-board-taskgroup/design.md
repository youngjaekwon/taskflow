## Context
Board & TaskGroup는 프로젝트 내 태스크를 시각적으로 그룹핑하는 칸반 보드 구조이다. 기존 Organization > Project 계층 아래에 Project > Board > TaskGroup 계층을 추가한다.

## Goals / Non-Goals
- Goals:
  - Board CRUD API 제공
  - TaskGroup CRUD + position 기반 순서 관리
  - 프로젝트 생성 시 기본 Board와 TaskGroup 자동 생성
- Non-Goals:
  - Task 모델 구현 (별도 변경으로 처리)
  - Board 간 TaskGroup 이동
  - Board/TaskGroup에 대한 별도 멤버 관리 (프로젝트 멤버십 재사용)

## Decisions

### Django 앱 구조
- **결정**: Board와 TaskGroup을 하나의 `boards` 앱에 배치
- **이유**: TaskGroup은 항상 Board 컨텍스트에서 존재하며 두 모델 간 결합도가 높음. 별도 앱 분리는 불필요한 복잡성 추가

### Position 관리 전략
- **결정**: `PositiveIntegerField`로 position 관리. 새 TaskGroup 생성 시 Board 내 `max(position) + 1` 할당. `reorderTaskGroups`는 전달받은 ID 목록 순서대로 0부터 재할당
- **대안 검토**: float 기반 position (삽입 시 중간값) → 구현 복잡성 대비 이점 부족. linked list → 쿼리 복잡성 증가. Board당 TaskGroup 수는 소규모(~10개)이므로 정수 재할당이 가장 단순하고 충분

### 기본 Board/TaskGroup 자동 생성
- **결정**: Django `post_save` signal 사용 (`created=True` 조건)
- **이유**: Project 생성 로직과 Board 생성 로직의 관심사 분리. boards 앱이 자체적으로 자동 생성 로직을 관리하므로 projects 앱 코드 수정 불필요
- **대안 검토**: createProject mutation에 직접 코드 추가 → 앱 간 결합도 증가, boards 앱 제거 시 projects 코드 수정 필요

### 권한 모델
- **결정**: 기존 `project_access_required` / `project_admin_required` 데코레이터를 Board 컨텍스트용으로 확장한 `board_access_required` / `board_admin_required` 데코레이터 신설
- **이유**: Board는 Project 하위 리소스이므로 동일한 권한 체계 적용이 자연스러움
- Board/TaskGroup 조회: project_access_required (프로젝트 멤버 또는 org ADMIN/OWNER)
- Board/TaskGroup 생성/수정/삭제/순서변경: project_admin_required (org ADMIN/OWNER만)
- 데코레이터가 input에서 board_id를 추출하여 Board > Project > Organization 경로로 권한 확인 후 `info.context`에 board, project, membership 주입

### Board slug
- **결정**: Board에 slug 필드 추가, Project 범위 내 unique
- **이유**: 기존 Organization, Project 모델과의 일관성 유지. URL-friendly 식별자 제공

## Risks / Trade-offs
- position 정수 재할당 방식은 Board당 TaskGroup 수가 소규모(~10개)이므로 bulk update 성능 이슈 없음
- signal 기반 자동 생성으로 인해 테스트에서 Project 생성 시마다 Board/TaskGroup이 함께 생성됨. 기존 프로젝트 테스트에서 이를 인지해야 하지만, Board 존재가 기존 테스트 로직에 영향을 주지는 않음

## Open Questions
- 없음
