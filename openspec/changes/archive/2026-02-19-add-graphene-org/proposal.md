# Change: backend-graphene에 Organization 서비스 추가

## Why

features.md P0 Organization 기능 8개와 관련 인가 기능을 구현하기 위해 `organizations` Django 앱을 신규 생성해야 한다. Organization은 프로젝트(Project), 보드(Board), 태스크(Task) 등 하위 도메인의 기반이 되는 핵심 엔티티이다.

## What Changes

- `organizations` Django 앱 신규 생성 (models, types, queries, mutations, permissions)
- Organization CRUD GraphQL API (생성/조회/수정/삭제)
- OrganizationMembership을 통한 멤버 관리 (초대, 역할 변경, 제거, 목록 조회)
- 역할 기반 접근 제어 시스템 (owner > admin > member 계층)
- 내가 속한 Organization 목록 조회

## Impact

- New spec: `graphene-org`
- Related spec: `graphene-auth` (인증된 사용자 기반, 기존 `@login_required` 데코레이터 활용)
- Affected code:
  - `config/schema.py` — 루트 스키마에 Organization query/mutation 추가
  - `config/settings/base.py` — INSTALLED_APPS에 `organizations` 추가
  - `organizations/` — 신규 앱 디렉터리 전체
