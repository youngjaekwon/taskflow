## Context

backend-graphene에 Organization 도메인을 신규 추가한다. 기존 `users` 앱의 패턴(types/queries/mutations/schema 분리, JWT 인증, `@login_required` 데코레이터)을 따르되, 역할 기반 권한 시스템을 새로 도입한다.

## Goals / Non-Goals

- Goals:
  - Organization CRUD + 멤버 관리 GraphQL API
  - owner > admin > member 역할 계층 기반 권한 시스템
  - 기존 users 앱 패턴과 일관된 코드 구조
- Non-Goals:
  - 이메일 초대 토큰 발송 (P0에서는 기존 등록 유저 직접 추가)
  - Organization soft delete / 아카이브 (P2 범위)

## Decisions

### 1. 모델 설계

**Organization 모델:**
- `name` (CharField, max_length=100) — Organization 이름
- `slug` (SlugField, unique=True) — URL-safe 식별자, `name`에서 자동 생성
- `description` (TextField, blank=True) — 설명
- `created_by` (FK → CustomUser) — 생성자 (감사 기록용, 권한 판단에는 사용하지 않음)
- `created_at`, `updated_at` — 타임스탬프

**OrganizationMembership 모델 (through table):**
- `organization` (FK → Organization)
- `user` (FK → CustomUser)
- `role` (CharField, choices: owner/admin/member) — 역할
- `invited_by` (FK → CustomUser, null=True) — 초대한 사용자 (owner 자신은 null)
- `joined_at` (DateTimeField, auto_now_add=True)
- unique_together: `(organization, user)` — 중복 멤버십 방지

### 2. 역할 계층

```
OWNER  (최고 권한) — Organization 삭제, 모든 멤버 관리, 역할 변경
ADMIN  (관리 권한) — 멤버 초대, member 역할 변경, member 제거
MEMBER (기본 권한) — 조회만 가능
```

| 작업 | OWNER | ADMIN | MEMBER |
|------|-------|-------|--------|
| Organization 조회 | O | O | O |
| Organization 수정 | O | O | X |
| Organization 삭제 | O | X | X |
| 멤버 초대 | O | O | X |
| 멤버 역할 변경 | O | O* | X |
| 멤버 제거 | O | O** | X |
| Ownership 이전 | O | X | X |
| 멤버 목록 조회 | O | O | O |

\* admin은 member ↔ admin 변경만 가능, owner 승격 불가. `updateMemberRole`로는 OWNER 역할 지정 불가 — `transferOwnership` 사용 필수.
\** admin은 member만 제거 가능, 다른 admin/owner 제거 불가

### 3. 멤버 초대 방식 (P0)

P0에서는 **기존 등록 유저 직접 추가** 방식을 사용한다:
- `inviteMember(organizationId, email)` → 이메일로 유저를 찾아 즉시 멤버십 생성
- 대상 유저가 시스템에 등록되어 있어야 함
- 미등록 이메일 → 에러 반환

**대안 (미채택):** 이메일 초대 토큰 발송 + 수락/거절 플로우 — 추가 모델(Invitation)과 이메일 템플릿이 필요하여 P0 범위를 초과함. 필요 시 P1에서 확장 가능.

### 4. 권한 유틸리티

기존 `@login_required` 패턴을 확장하여 Organization 전용 데코레이터를 만든다:
- `@org_member_required` — Organization 소속 확인
- `@org_role_required(min_role=Role.ADMIN)` — 최소 역할 확인

Mutation/Query resolver에서 `organization_id` 인자를 기반으로 멤버십과 역할을 검증한다.

### 5. GraphQL 스키마

**Types:**
- `OrganizationType` (DjangoObjectType) — Organization 모델 매핑
- `OrganizationMemberType` (DjangoObjectType) — Membership + User 정보
- Input types: `CreateOrganizationInput`, `UpdateOrganizationInput`, `InviteMemberInput`, `UpdateMemberRoleInput`, `RemoveMemberInput`, `TransferOwnershipInput`

**Queries:**
- `organization(id: ID!)` — 단일 Organization 상세 (소속 멤버만)
- `myOrganizations` — 내가 속한 Organization 목록

**Mutations:**
- `createOrganization(input)` — 생성 (생성자 자동 OWNER)
- `updateOrganization(input)` — 수정 (ADMIN 이상)
- `deleteOrganization(id)` — 삭제 (OWNER만)
- `inviteMember(input)` — 멤버 추가 (ADMIN 이상)
- `updateMemberRole(input)` — 역할 변경 (ADMIN 이상, 조건부)
- `removeMember(input)` — 멤버 제거 (ADMIN 이상, 조건부)
- `transferOwnership(input)` — Ownership 이전 (OWNER만, 대상을 OWNER로 승격 + 본인을 ADMIN으로 강등, 원자적 처리)

### 6. Slug 생성

Django `slugify(name)`으로 자동 생성한다. 중복 시 `-2`, `-3` 등의 접미사를 추가하여 유일성을 보장한다.

### 7. Organization 삭제

P0에서는 hard delete를 사용한다. `CASCADE`로 관련 멤버십도 함께 삭제된다. Soft delete/아카이브는 P2 범위(features.md P2 기타 #4).

## Risks / Trade-offs

- **직접 추가 방식의 한계**: 초대받는 사용자의 동의 없이 멤버십이 생성됨. P0에서는 학습 프로젝트 특성상 수용 가능하나, 프로덕션에서는 초대+수락 플로우가 필요함.
- **Hard delete**: Organization 삭제 시 하위 데이터(향후 Project, Task 등)가 모두 삭제됨. P2에서 soft delete로 전환 예정.
- **Owner 유일성**: 한 Organization에 OWNER가 반드시 1명 이상 존재해야 함. OWNER가 자신을 제거하거나 역할을 강등하는 것을 방지해야 함.

## Open Questions

- 없음 (모든 주요 결정 사항이 위에 문서화됨)
