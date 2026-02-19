# graphene-org Specification

## Purpose
TBD - created by archiving change add-graphene-org. Update Purpose after archive.
## Requirements
### Requirement: Organization Creation

The system SHALL allow authenticated users to create a new Organization via `createOrganization` mutation.
The system SHALL auto-generate a unique slug from the Organization name.
The system SHALL automatically create an OWNER membership for the creator upon Organization creation.

#### Scenario: Organization creation success

- **GIVEN** 인증된 사용자가 유효한 Organization 이름을 제공한 경우
- **WHEN** `createOrganization` mutation을 호출하면
- **THEN** 새 Organization이 생성된다
- **AND** 이름 기반으로 slug가 자동 생성된다
- **AND** 생성자가 OWNER 역할로 멤버십에 추가된다
- **AND** 생성된 Organization 정보가 반환된다

#### Scenario: Organization creation with duplicate slug

- **GIVEN** 동일한 이름에서 파생된 slug가 이미 존재하는 경우
- **WHEN** `createOrganization` mutation을 호출하면
- **THEN** slug에 숫자 접미사가 추가되어 유일성이 보장된다

#### Scenario: Organization creation without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createOrganization` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

#### Scenario: Organization creation with empty name

- **GIVEN** 빈 문자열이 Organization 이름으로 제공된 경우
- **WHEN** `createOrganization` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

---

### Requirement: Organization Retrieval and Update

The system SHALL allow Organization members to view Organization details via `organization(id)` query.
The system SHALL allow ADMIN or OWNER to update Organization information (name, description) via `updateOrganization` mutation.
The system SHALL deny access to non-members.

#### Scenario: Organization detail retrieval success

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버인 경우
- **WHEN** `organization(id)` query를 호출하면
- **THEN** Organization 상세 정보(id, name, slug, description, members, timestamps)가 반환된다

#### Scenario: Organization detail retrieval by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `organization(id)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Organization update success

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 또는 OWNER인 경우
- **WHEN** `updateOrganization` mutation을 호출하면
- **THEN** Organization 정보가 업데이트되고 갱신된 정보가 반환된다

#### Scenario: Organization update by MEMBER role

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `updateOrganization` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Organization update without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateOrganization` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Organization Deletion

The system SHALL allow only the OWNER to delete an Organization via `deleteOrganization` mutation.
The system SHALL cascade-delete all related memberships when an Organization is deleted.

#### Scenario: Organization deletion by OWNER

- **GIVEN** 인증된 사용자가 해당 Organization의 OWNER인 경우
- **WHEN** `deleteOrganization` mutation을 호출하면
- **THEN** Organization과 관련 멤버십이 삭제된다
- **AND** 성공 응답이 반환된다

#### Scenario: Organization deletion by ADMIN

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN인 경우
- **WHEN** `deleteOrganization` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Organization deletion by MEMBER

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER인 경우
- **WHEN** `deleteOrganization` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Organization deletion by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `deleteOrganization` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

---

### Requirement: Member Invitation

The system SHALL allow ADMIN or OWNER to add an existing registered user to the Organization by email via `inviteMember` mutation.
The system SHALL assign MEMBER role by default to newly invited users.

#### Scenario: Member invitation success

- **GIVEN** ADMIN 이상 역할의 사용자가 시스템에 등록된 유저의 이메일을 제공한 경우
- **WHEN** `inviteMember` mutation을 호출하면
- **THEN** 해당 유저가 MEMBER 역할로 Organization에 추가된다
- **AND** 추가된 멤버 정보가 반환된다

#### Scenario: Member invitation with non-existent email

- **GIVEN** 시스템에 등록되지 않은 이메일이 제공된 경우
- **WHEN** `inviteMember` mutation을 호출하면
- **THEN** 해당 이메일의 유저를 찾을 수 없다는 에러가 반환된다

#### Scenario: Member invitation for already existing member

- **GIVEN** 이미 해당 Organization의 멤버인 유저의 이메일이 제공된 경우
- **WHEN** `inviteMember` mutation을 호출하면
- **THEN** 이미 멤버라는 에러가 반환된다

#### Scenario: Member invitation by MEMBER role

- **GIVEN** MEMBER 역할의 사용자가 초대를 시도하는 경우
- **WHEN** `inviteMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Member invitation without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `inviteMember` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Member Role Management

The system SHALL allow ADMIN or OWNER to change a member's role via `updateMemberRole` mutation.
The system SHALL NOT allow setting a member's role to OWNER via `updateMemberRole` — ownership transfer MUST use the dedicated `transferOwnership` mutation.
The system SHALL prevent ADMIN from promoting a member to OWNER.
The system SHALL prevent users from changing their own role.

#### Scenario: OWNER changes member role to ADMIN

- **GIVEN** OWNER가 MEMBER 역할의 멤버를 대상으로 ADMIN 역할을 지정한 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 대상 멤버의 역할이 ADMIN으로 변경된다

#### Scenario: OWNER demotes ADMIN to MEMBER

- **GIVEN** OWNER가 ADMIN 역할의 멤버를 대상으로 MEMBER 역할을 지정한 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 대상 멤버의 역할이 MEMBER로 변경된다

#### Scenario: ADMIN changes member role

- **GIVEN** ADMIN이 MEMBER 역할의 멤버를 대상으로 ADMIN 역할을 지정한 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 대상 멤버의 역할이 ADMIN으로 변경된다

#### Scenario: Attempt to set OWNER role via updateMemberRole

- **GIVEN** OWNER가 다른 멤버를 대상으로 OWNER 역할을 지정한 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** OWNER 역할은 `transferOwnership`을 사용해야 한다는 에러가 반환된다

#### Scenario: ADMIN attempts to promote to OWNER

- **GIVEN** ADMIN이 멤버를 대상으로 OWNER 역할을 지정한 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: User attempts to change own role

- **GIVEN** 사용자가 자기 자신의 역할을 변경하려는 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 자신의 역할은 변경할 수 없다는 에러가 반환된다

#### Scenario: MEMBER attempts to change role

- **GIVEN** MEMBER 역할의 사용자가 역할 변경을 시도하는 경우
- **WHEN** `updateMemberRole` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

---

### Requirement: Member Removal

The system SHALL allow ADMIN or OWNER to remove a member from the Organization via `removeMember` mutation.
The system SHALL prevent ADMIN from removing other ADMINs or the OWNER.
The system SHALL prevent the sole OWNER from being removed.

#### Scenario: OWNER removes a MEMBER

- **GIVEN** OWNER가 MEMBER 역할의 멤버를 대상으로 제거를 요청한 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 대상 멤버의 멤버십이 삭제된다

#### Scenario: OWNER removes an ADMIN

- **GIVEN** OWNER가 ADMIN 역할의 멤버를 대상으로 제거를 요청한 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 대상 멤버의 멤버십이 삭제된다

#### Scenario: ADMIN removes a MEMBER

- **GIVEN** ADMIN이 MEMBER 역할의 멤버를 대상으로 제거를 요청한 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 대상 멤버의 멤버십이 삭제된다

#### Scenario: ADMIN attempts to remove another ADMIN

- **GIVEN** ADMIN이 다른 ADMIN 역할의 멤버를 대상으로 제거를 요청한 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: ADMIN attempts to remove OWNER

- **GIVEN** ADMIN이 OWNER 역할의 멤버를 대상으로 제거를 요청한 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Attempt to remove sole OWNER

- **GIVEN** Organization에 OWNER가 1명뿐이고 해당 OWNER를 제거하려는 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 유일한 OWNER는 제거할 수 없다는 에러가 반환된다

#### Scenario: MEMBER attempts to remove another member

- **GIVEN** MEMBER 역할의 사용자가 멤버 제거를 시도하는 경우
- **WHEN** `removeMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

---

### Requirement: Ownership Transfer

The system SHALL allow the current OWNER to transfer ownership to another member via `transferOwnership` mutation.
The system SHALL atomically promote the target member to OWNER and demote the current OWNER to ADMIN.
The system SHALL only allow the OWNER to perform this operation.

#### Scenario: Ownership transfer success

- **GIVEN** OWNER가 Organization의 다른 멤버를 대상으로 ownership 이전을 요청한 경우
- **WHEN** `transferOwnership` mutation을 호출하면
- **THEN** 대상 멤버의 역할이 OWNER로 변경된다
- **AND** 기존 OWNER의 역할이 ADMIN으로 변경된다
- **AND** 두 변경이 원자적으로 처리된다

#### Scenario: Ownership transfer by ADMIN

- **GIVEN** ADMIN 역할의 사용자가 ownership 이전을 시도하는 경우
- **WHEN** `transferOwnership` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Ownership transfer by MEMBER

- **GIVEN** MEMBER 역할의 사용자가 ownership 이전을 시도하는 경우
- **WHEN** `transferOwnership` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Ownership transfer to non-member

- **GIVEN** OWNER가 Organization의 멤버가 아닌 유저를 대상으로 ownership 이전을 요청한 경우
- **WHEN** `transferOwnership` mutation을 호출하면
- **THEN** 대상 유저가 멤버가 아니라는 에러가 반환된다

#### Scenario: Ownership transfer to self

- **GIVEN** OWNER가 자기 자신을 대상으로 ownership 이전을 요청한 경우
- **WHEN** `transferOwnership` mutation을 호출하면
- **THEN** 자기 자신에게는 이전할 수 없다는 에러가 반환된다

---

### Requirement: Member List Retrieval

The system SHALL allow Organization members to view the member list with role information.
The system SHALL deny member list access to non-members.

#### Scenario: Member list retrieval success

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버인 경우
- **WHEN** `organization(id)` query에서 members 필드를 요청하면
- **THEN** 멤버 목록(유저 정보, 역할, 가입일)이 반환된다

#### Scenario: Member list retrieval by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `organization(id)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

---

### Requirement: My Organizations Retrieval

The system SHALL allow authenticated users to retrieve a list of Organizations they belong to via `myOrganizations` query.
The system SHALL include the user's role in each Organization.

#### Scenario: My Organizations retrieval success

- **GIVEN** 인증된 사용자가 1개 이상의 Organization에 소속된 경우
- **WHEN** `myOrganizations` query를 호출하면
- **THEN** 소속된 모든 Organization 목록이 반환된다
- **AND** 각 Organization에서의 사용자 역할이 포함된다

#### Scenario: My Organizations retrieval with no memberships

- **GIVEN** 인증된 사용자가 어떤 Organization에도 소속되지 않은 경우
- **WHEN** `myOrganizations` query를 호출하면
- **THEN** 빈 목록이 반환된다

#### Scenario: My Organizations retrieval without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `myOrganizations` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Organization Access Control

The system SHALL enforce a role hierarchy of OWNER > ADMIN > MEMBER for all Organization operations.
The system SHALL deny all access to Organization resources for non-members.
The system SHALL require authentication for all Organization endpoints.

#### Scenario: Role hierarchy enforcement

- **GIVEN** 특정 작업에 ADMIN 이상 권한이 필요한 경우
- **WHEN** MEMBER 역할의 사용자가 해당 작업을 시도하면
- **THEN** 권한 부족 에러가 반환된다
- **AND** ADMIN 또는 OWNER 역할의 사용자는 해당 작업을 수행할 수 있다

#### Scenario: Non-member access denial

- **GIVEN** 인증된 사용자가 특정 Organization의 멤버가 아닌 경우
- **WHEN** 해당 Organization의 리소스에 접근하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Unauthenticated access denial

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** Organization 관련 query 또는 mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

