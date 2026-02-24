# Change: Add Task service to backend-graphene

## Why

Board와 TaskGroup 구현이 완료되었으므로, 핵심 도메인인 Task CRUD, 상태/담당자 관리, 필터링, 페이지네이션을 구현하여 태스크 관리 기능을 완성한다.

## What Changes

- **새 Django 앱**: `tasks` 앱 생성 (Task 모델, GraphQL 타입/쿼리/뮤테이션)
- **Task 모델**: title, description, status, priority, assignee, due_date, task_group, position 필드
- **GraphQL 뮤테이션**: createTask, updateTask, deleteTask, moveTask, reorderTasks, assignTask
- **GraphQL 쿼리**: task (단건 조회), tasks (목록 조회 + 복합 필터링 + 페이지네이션)
- **권한 제어**: Task 삭제는 생성자 또는 Org ADMIN 이상만 가능
- **TaskGroupType 확장**: tasks 필드 추가 (graphene-board 스펙 수정)

## Impact

- Affected specs: `graphene-task` (신규), `graphene-board` (TaskGroupType에 tasks 필드 추가)
- Affected code: `apps/backend-graphene/tasks/` (신규), `apps/backend-graphene/boards/types.py`, `apps/backend-graphene/config/schema.py`
