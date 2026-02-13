# Change: backend-graphene P0 인증 서비스 추가

## Why

TaskFlow 백엔드(Graphene)에 사용자 인증 기능이 없어 어떤 보호된 API도 사용할 수 없다. P0 핵심 기능인 인증 서비스를 구현하여 회원가입, 로그인, 토큰 관리, 프로필 관리, 비밀번호 관리, 이메일 인증을 지원해야 한다.

## What Changes

- Django 프로젝트 초기화 (`config/`, `manage.py`, settings 분리)
- 커스텀 User 모델 및 Profile 필드 구현
- JWT 기반 인증 REST API (`/api/v1/auth/...`): 로그인, 토큰 리프레시, 로그아웃
- 이메일/비밀번호 회원가입 REST API (형식 검증, 비밀번호 강도 규칙)
- 이메일 인증 플로우 REST API (활성화 토큰 발송 및 검증)
- 비밀번호 변경 및 초기화 플로우 REST API
- 프로필 조회/수정 GraphQL 스키마 (`me` query, `updateProfile` mutation)
- 프로필 이미지 업로드 RESTful API (`PUT/DELETE /api/v1/users/me/profile-image`)
- 전체 기능에 대한 테스트 (TDD)

## Impact

- Affected specs: `graphene-auth` (신규)
- Affected code: `apps/backend-graphene/` 전체 (Django 프로젝트 초기화부터)
- Dependencies: Django, graphene-django, djangorestframework, djangorestframework-simplejwt, Pillow
