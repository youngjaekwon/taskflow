# Change: Add Label service to backend-graphene

## Why

features.md P1 Label 섹션의 4가지 기능(Label CRUD, 색상 코드 지정, Task-Label 연결, Label 필터링)을 backend-graphene에 구현한다. Label은 Organization 레벨에서 공유되는 분류 체계로, Task에 M2M 관계로 연결하여 다중 라벨링 및 필터링을 지원한다.

## What Changes

- **새 Django 앱 `labels`**: Label 모델, GraphQL 타입/쿼리/뮤테이션 추가
- **Label 모델**: Organization FK, name, color(hex), unique_together(organization, name)
- **Task-Label M2M**: Task 모델에 `labels` ManyToManyField 추가
- **Label CRUD 뮤테이션**: createLabel, updateLabel, deleteLabel (Org ADMIN+ 권한)
- **Task-Label 관계 뮤테이션**: addLabelsToTask, removeLabelsFromTask (Project 접근 권한)
- **Label 목록 쿼리**: labels(organizationId) — Org 멤버 조회
- **Task 필터 확장**: TaskFilterInput에 label_ids 필터 추가
- **TaskType 확장**: labels 필드 추가

## Impact

- Affected specs: `graphene-label` (신규), `graphene-task` (수정 — Task 필터링에 label_ids 추가, TaskType에 labels 필드 추가)
- Affected code: `labels/` (신규 앱), `tasks/models.py`, `tasks/types.py`, `tasks/queries.py`, `config/schema.py`, `config/settings/base.py`
