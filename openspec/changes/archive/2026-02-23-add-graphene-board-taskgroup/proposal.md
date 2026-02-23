# Change: Board & TaskGroup 서비스 추가 (backend-graphene)

## Why
프로젝트 내에서 칸반 스타일의 태스크 관리를 지원하기 위해 Board와 TaskGroup(컬럼) 모델 및 GraphQL API가 필요하다. Board는 프로젝트당 복수 개 생성 가능하며, TaskGroup은 Board 내 시각적 그룹핑 단위로 Task status와 독립적으로 관리된다.

## What Changes
- Board 모델 및 CRUD GraphQL API 신설 (`boards` Django 앱)
- TaskGroup 모델 및 CRUD GraphQL API 신설 (동일 `boards` 앱)
- TaskGroup position 기반 순서 관리 및 `reorderTaskGroups` mutation
- 프로젝트 생성 시 기본 Board + 4개 TaskGroup 자동 생성 (Django signal)
- graphene-project 스펙의 Project Creation 요구사항 수정 (자동 생성 추가)

## Impact
- Affected specs: `graphene-board` (신규), `graphene-project` (수정)
- Affected code: `apps/backend-graphene/boards/` (신규), `apps/backend-graphene/config/schema.py`, `apps/backend-graphene/config/settings/base.py`
