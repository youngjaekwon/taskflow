## 0. 앱 스캐폴딩
- [ ] 0.1 `boards` Django 앱 생성 (`python manage.py startapp boards`)
- [ ] 0.2 `boards/tests/` 패키지 구조 생성 (`__init__.py`, `factories.py`, `conftest.py`)
- [ ] 0.3 `settings/base.py` INSTALLED_APPS에 `boards` 추가

## 1. Board 모델 (RED → GREEN)
- [ ] 1.1 `factories.py` — BoardFactory 작성 (기대하는 모델 인터페이스 정의)
- [ ] 1.2 `conftest.py` — register(BoardFactory), 복합 fixture 작성 (org_with_owner, project_with_member 등)
- [ ] 1.3 `test_models.py` — TestBoardModel 테스트 작성 (RED)
  - slug 자동 생성, Project 범위 내 slug unique, duplicate slug 접미사, `__str__`, cascade delete
- [ ] 1.4 Board 모델 구현 → 테스트 통과 확인 (GREEN)

## 2. TaskGroup 모델 (RED → GREEN)
- [ ] 2.1 `factories.py` — TaskGroupFactory 추가
- [ ] 2.2 `conftest.py` — register(TaskGroupFactory)
- [ ] 2.3 `test_models.py` — TestTaskGroupModel 테스트 작성 (RED)
  - position 기본값, ordering by position, Board cascade delete, `__str__`
- [ ] 2.4 TaskGroup 모델 구현 → 테스트 통과 확인 (GREEN)
- [ ] 2.5 마이그레이션 생성 및 적용

## 3. 기본 Board/TaskGroup 자동 생성 Signal (RED → GREEN)
- [ ] 3.1 `test_signals.py` — TestDefaultBoardCreation 테스트 작성 (RED)
  - Project 생성 시 "Main Board" + 4개 TaskGroup(To Do/In Progress/In Review/Done) 자동 생성
  - created_by가 Project의 created_by와 동일
  - TaskGroup position 순서 검증 (0, 1, 2, 3)
  - Project 수정 시 추가 생성 없음
- [ ] 3.2 `signals.py` + `apps.py` ready() — post_save signal 구현 → 테스트 통과 확인 (GREEN)
- [ ] 3.3 기존 프로젝트 테스트 전체 실행하여 영향 없는지 확인

## 4. Board 쿼리 (RED → GREEN)
- [ ] 4.1 `test_queries.py` — TestBoardDetailQuery 테스트 작성 (RED)
  - 프로젝트 멤버 조회 성공, Org ADMIN 조회 성공
  - taskGroups position 오름차순 정렬 검증
  - 비프로젝트 멤버 MEMBER 차단, 비Org 멤버 차단, 미인증 차단
- [ ] 4.2 `test_queries.py` — TestBoardListQuery 테스트 작성 (RED)
  - 프로젝트 멤버 목록 조회, 비Org 멤버 차단, 미인증 차단
- [ ] 4.3 `types.py` — BoardType, TaskGroupType 정의
- [ ] 4.4 `decorators.py` — board_access_required, board_admin_required 구현
- [ ] 4.5 `queries.py` — board, boards 쿼리 구현
- [ ] 4.6 `config/schema.py`에 BoardQuery 통합 → 테스트 통과 확인 (GREEN)

## 5. Board Mutations (RED → GREEN, mutation별 반복)
- [ ] 5.1 `test_mutations.py` — TestCreateBoard 테스트 작성 (RED)
  - 성공, slug 중복 처리, MEMBER 차단, 비Org 멤버 차단, 미인증 차단, 빈 이름 검증
- [ ] 5.2 CreateBoard mutation 구현 → 테스트 통과 확인 (GREEN)
- [ ] 5.3 `test_mutations.py` — TestUpdateBoard 테스트 작성 (RED)
  - 성공, MEMBER 차단, 미인증 차단
- [ ] 5.4 UpdateBoard mutation 구현 → 테스트 통과 확인 (GREEN)
- [ ] 5.5 `test_mutations.py` — TestDeleteBoard 테스트 작성 (RED)
  - 성공 + TaskGroup cascade 삭제, MEMBER 차단, 비Org 멤버 차단, 미인증 차단
- [ ] 5.6 DeleteBoard mutation 구현
- [ ] 5.7 `config/schema.py`에 BoardMutation 통합 → 테스트 통과 확인 (GREEN)

## 6. TaskGroup Mutations (RED → GREEN, mutation별 반복)
- [ ] 6.1 `test_taskgroup_mutations.py` — TestCreateTaskGroup 테스트 작성 (RED)
  - 성공 + auto-position, 빈 Board에서 position=0, MEMBER 차단, 미인증 차단
- [ ] 6.2 CreateTaskGroup mutation 구현 → 테스트 통과 확인 (GREEN)
- [ ] 6.3 `test_taskgroup_mutations.py` — TestUpdateTaskGroup 테스트 작성 (RED)
  - 성공, MEMBER 차단, 미인증 차단
- [ ] 6.4 UpdateTaskGroup mutation 구현 → 테스트 통과 확인 (GREEN)
- [ ] 6.5 `test_taskgroup_mutations.py` — TestDeleteTaskGroup 테스트 작성 (RED)
  - 성공, MEMBER 차단, 미인증 차단
- [ ] 6.6 DeleteTaskGroup mutation 구현 → 테스트 통과 확인 (GREEN)
- [ ] 6.7 `test_taskgroup_mutations.py` — TestReorderTaskGroups 테스트 작성 (RED)
  - 성공 (position 재할당 검증), 불완전 ID 목록, 다른 Board의 ID, MEMBER 차단
- [ ] 6.8 ReorderTaskGroups mutation 구현 → 테스트 통과 확인 (GREEN)

## 7. 최종 검증
- [ ] 7.1 전체 테스트 실행 (`pnpm test --filter @taskflow/backend-graphene`)
- [ ] 7.2 린트 통과 확인 (`pnpm lint --filter @taskflow/backend-graphene`)
