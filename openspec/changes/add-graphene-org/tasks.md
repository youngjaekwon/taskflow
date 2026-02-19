## 1. App Setup & Models

- [ ] 1.1 `organizations` Django 앱 생성 및 `INSTALLED_APPS` 등록
- [ ] 1.2 `Organization` 모델 정의 (name, slug, description, created_by, timestamps)
- [ ] 1.3 `OrganizationMembership` 모델 정의 (organization, user, role, invited_by, joined_at)
- [ ] 1.4 역할 enum 정의 (OWNER, ADMIN, MEMBER)
- [ ] 1.5 마이그레이션 생성 및 실행

## 2. Permission Utilities

- [ ] 2.1 Organization 멤버십/역할 확인 헬퍼 함수 작성
- [ ] 2.2 `@org_member_required` 데코레이터 작성 (소속 확인)
- [ ] 2.3 `@org_role_required(min_role)` 데코레이터 작성 (최소 역할 확인)

## 3. GraphQL Types

- [ ] 3.1 `OrganizationType` (DjangoObjectType) 정의
- [ ] 3.2 `OrganizationMemberType` (DjangoObjectType) 정의
- [ ] 3.3 Input types 정의 (Create, Update, InviteMember, UpdateMemberRole, RemoveMember)

## 4. GraphQL Queries

- [ ] 4.1 `myOrganizations` query 구현 (내 Organization 목록)
- [ ] 4.2 `organization(id)` query 구현 (상세 조회, 소속 멤버만)

## 5. GraphQL Mutations — Organization CRUD

- [ ] 5.1 `createOrganization` mutation 구현 (생성자 자동 OWNER)
- [ ] 5.2 `updateOrganization` mutation 구현 (ADMIN 이상)
- [ ] 5.3 `deleteOrganization` mutation 구현 (OWNER만)

## 6. GraphQL Mutations — Member Management

- [ ] 6.1 `inviteMember` mutation 구현 (이메일로 기존 유저 추가, ADMIN 이상)
- [ ] 6.2 `updateMemberRole` mutation 구현 (역할 변경, 조건부 권한)
- [ ] 6.3 `removeMember` mutation 구현 (멤버 제거, 조건부 권한)
- [ ] 6.4 `transferOwnership` mutation 구현 (OWNER만, 원자적 역할 교체)

## 7. Root Schema Integration

- [ ] 7.1 `config/schema.py`에 OrganizationQuery, OrganizationMutation 통합

## 8. Tests

- [ ] 8.1 모델 테스트 (Organization/Membership 생성, 유일성 제약, slug 자동 생성)
- [ ] 8.2 권한 유틸리티 테스트 (데코레이터, 역할 계층 검증)
- [ ] 8.3 Query 테스트 (myOrganizations, organization 상세, 비소속 유저 차단)
- [ ] 8.4 Mutation 테스트 — CRUD (생성/수정/삭제 + 권한 검증)
- [ ] 8.5 Mutation 테스트 — 멤버 관리 (초대/역할 변경/제거/ownership 이전 + 권한 검증)
