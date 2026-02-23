# Change: Add Project Service to backend-graphene

## Why

features.md P0 Project 기능 구현이 필요하다. Organization 하위에 프로젝트를 생성·관리하고, Organization 멤버 중 프로젝트 멤버를 선택적으로 할당하여 프로젝트별 접근 제한을 구현한다. 이는 Board & Task 기능의 전제 조건이다.

## What Changes

- **Project 모델 추가**: Organization에 종속되는 Project 모델과 ProjectMembership through 모델
- **GraphQL 스키마 추가**: Project CRUD query/mutation 및 멤버 관리 mutation
- **프로젝트 권한 체계 구현**: Organization 역할 기반 + ProjectMembership 기반 이중 접근 제어
  - Organization ADMIN 이상: 모든 프로젝트 접근 및 관리 가능
  - Organization MEMBER: 할당된 프로젝트만 접근 가능
- **루트 스키마 통합**: config/schema.py에 ProjectQuery, ProjectMutation 추가

## Impact

- Affected specs: `graphene-project` (신규)
- Affected code:
  - `apps/backend-graphene/projects/` (신규 Django 앱)
  - `apps/backend-graphene/config/schema.py` (루트 스키마 확장)
  - `apps/backend-graphene/config/settings/base.py` (INSTALLED_APPS 추가)
