## 0. 앱 스캐폴딩

- [ ] 0.1 `tasks` Django 앱 생성 (`python manage.py startapp tasks`)
- [ ] 0.2 `config/settings/base.py`의 `INSTALLED_APPS`에 `tasks` 추가
- [ ] 0.3 `tasks/tests/` 디렉토리 구조 생성 (`__init__.py`, `conftest.py`, `factories.py`)

## 1. Task 모델 (RED → GREEN)

- [ ] 1.1 `TaskFactory` 작성 (`tasks/tests/factories.py`)
- [ ] 1.2 모델 테스트 작성 (`tasks/tests/test_models.py`) — 필드 기본값, 제약조건, ordering
- [ ] 1.3 `Task` 모델 구현 (`tasks/models.py`) — TaskStatus, TaskPriority TextChoices, Task 모델
- [ ] 1.4 마이그레이션 생성 및 적용 (`python manage.py makemigrations tasks`)
- [ ] 1.5 테스트 통과 확인

## 2. GraphQL 타입 및 데코레이터

- [ ] 2.1 `TaskType`, `TaskStatusEnum`, `TaskPriorityEnum` 정의 (`tasks/types.py`)
- [ ] 2.2 Input 타입 정의 — `CreateTaskInput`, `UpdateTaskInput`, `MoveTaskInput`, `ReorderTasksInput`, `AssignTaskInput`, `TaskFilterInput`, `PaginationInput`
- [ ] 2.3 `TaskConnection` 타입 정의 (tasks, totalCount, hasNext, hasPrevious)
- [ ] 2.4 `tasks/decorators.py` — task 접근 권한 데코레이터 (`task_access_required`, `task_delete_permission_required`)
- [ ] 2.5 `boards/types.py`의 `TaskGroupType`에 `tasks` 리졸버 추가

## 3. createTask 뮤테이션 (RED → GREEN)

- [ ] 3.1 테스트 작성 (`tasks/tests/test_mutations.py: TestCreateTask`) — 성공, 담당자 지정, Project 비멤버 담당자, 빈 제목, 권한 없음, 미인증
- [ ] 3.2 `CreateTask` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 3.3 테스트 통과 확인

## 4. updateTask 뮤테이션 (RED → GREEN)

- [ ] 4.1 테스트 작성 (`tasks/tests/test_mutations.py: TestUpdateTask`) — 성공(부분 업데이트), 상태 변경, 권한 없음, 존재하지 않는 Task
- [ ] 4.2 `UpdateTask` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 4.3 테스트 통과 확인

## 5. deleteTask 뮤테이션 (RED → GREEN)

- [ ] 5.1 테스트 작성 (`tasks/tests/test_mutations.py: TestDeleteTask`) — 생성자 삭제, ADMIN 삭제, MEMBER 비생성자 삭제 거부, 미인증
- [ ] 5.2 `DeleteTask` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 5.3 테스트 통과 확인

## 6. moveTask 뮤테이션 (RED → GREEN)

- [ ] 6.1 테스트 작성 (`tasks/tests/test_mutations.py: TestMoveTask`) — 다른 TaskGroup 이동, position 미지정, 다른 Board TaskGroup 이동 거부
- [ ] 6.2 `MoveTask` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 6.3 테스트 통과 확인

## 7. reorderTasks 뮤테이션 (RED → GREEN)

- [ ] 7.1 테스트 작성 (`tasks/tests/test_mutations.py: TestReorderTasks`) — 순서 변경 성공, 다른 TaskGroup Task ID 포함 시 에러
- [ ] 7.2 `ReorderTasks` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 7.3 테스트 통과 확인

## 8. assignTask 뮤테이션 (RED → GREEN)

- [ ] 8.1 테스트 작성 (`tasks/tests/test_mutations.py: TestAssignTask`) — 담당자 지정, 담당자 해제, Project 비멤버 지정 거부
- [ ] 8.2 `AssignTask` 뮤테이션 구현 (`tasks/mutations.py`)
- [ ] 8.3 테스트 통과 확인

## 9. task 단건 쿼리 (RED → GREEN)

- [ ] 9.1 테스트 작성 (`tasks/tests/test_queries.py: TestTaskDetail`) — 성공, 권한 없음, 존재하지 않는 Task
- [ ] 9.2 `TaskQuery` 구현 (`tasks/queries.py`) — `task(id)` resolver
- [ ] 9.3 테스트 통과 확인

## 10. tasks 목록 쿼리 + 필터링 + 페이지네이션 (RED → GREEN)

- [ ] 10.1 테스트 작성 (`tasks/tests/test_queries.py: TestTaskList`) — 목록 조회, 상태 필터, 우선순위 필터, 담당자 필터, 기한 범위 필터, 키워드 검색
- [ ] 10.2 테스트 작성 (`tasks/tests/test_queries.py: TestTaskPagination`) — 페이지네이션 기본, 다음 페이지, 기본값 적용
- [ ] 10.3 `TaskQuery` 구현 (`tasks/queries.py`) — `tasks(projectId, filter, pagination)` resolver
- [ ] 10.4 테스트 통과 확인

## 11. TaskGroup 삭제 방어 (RED → GREEN)

- [ ] 11.1 테스트 작성 (`boards/tests/test_taskgroup_mutations.py`) — Task 있는 TaskGroup 삭제 거부 테스트
- [ ] 11.2 `boards/mutations.py`의 `DeleteTaskGroup`에 Task 존재 검증 추가
- [ ] 11.3 테스트 통과 확인

## 12. 스키마 통합 및 최종 검증

- [ ] 12.1 `tasks/schema.py` 작성 — TaskQuery, TaskMutation 조합
- [ ] 12.2 `config/schema.py`에 TaskQuery, TaskMutation 통합
- [ ] 12.3 전체 테스트 실행 (`pytest`) — 기존 테스트 포함 모두 통과 확인
- [ ] 12.4 린트 실행 (`ruff check`, `ruff format`)
