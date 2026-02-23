## ADDED Requirements

### Requirement: Project Creation

The system SHALL allow Organization ADMIN or OWNER to create a new Project under an Organization via `createProject` mutation.
The system SHALL auto-generate a unique slug from the Project name within the Organization scope.
The system SHALL automatically add the creator as a ProjectMembership upon Project creation.

#### Scenario: Project creation success

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createProject` mutation을 유효한 프로젝트 이름과 Organization ID로 호출하면
- **THEN** 새 Project가 해당 Organization 하위에 생성된다
- **AND** 이름 기반으로 slug가 자동 생성된다
- **AND** 생성자가 ProjectMembership에 자동 추가된다
- **AND** 생성된 Project 정보가 반환된다

#### Scenario: Project creation with duplicate slug in same organization

- **GIVEN** 동일한 Organization 내에서 같은 이름에서 파생된 slug가 이미 존재하는 경우
- **WHEN** `createProject` mutation을 호출하면
- **THEN** slug에 숫자 접미사가 추가되어 Organization 내 유일성이 보장된다

#### Scenario: Project creation by MEMBER role

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `createProject` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Project creation by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `createProject` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Project creation without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createProject` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

#### Scenario: Project creation with empty name

- **GIVEN** 빈 문자열이 프로젝트 이름으로 제공된 경우
- **WHEN** `createProject` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

---

### Requirement: Project Retrieval and Update

The system SHALL allow project members and Organization ADMIN/OWNER to view Project details via `project(id)` query.
The system SHALL allow Organization ADMIN or OWNER to update Project information (name, description) via `updateProject` mutation.
The system SHALL deny access to Organization MEMBERs who are not assigned to the Project.

#### Scenario: Project detail retrieval by project member

- **GIVEN** 인증된 사용자가 해당 프로젝트의 멤버인 경우
- **WHEN** `project(id)` query를 호출하면
- **THEN** Project 상세 정보(id, name, slug, description, organization, members, timestamps)가 반환된다

#### Scenario: Project detail retrieval by Organization ADMIN

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상이지만 프로젝트 멤버가 아닌 경우
- **WHEN** `project(id)` query를 호출하면
- **THEN** Project 상세 정보가 반환된다

#### Scenario: Project detail retrieval by non-project-member MEMBER

- **GIVEN** 인증된 사용자가 Organization MEMBER이지만 해당 프로젝트의 멤버가 아닌 경우
- **WHEN** `project(id)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Project detail retrieval by non-organization-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `project(id)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Project update success

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateProject` mutation을 호출하면
- **THEN** Project 정보가 업데이트되고 갱신된 정보가 반환된다

#### Scenario: Project update by MEMBER role

- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우 (프로젝트 멤버 여부 무관)
- **WHEN** `updateProject` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Project update without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateProject` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Project Deletion

The system SHALL allow Organization ADMIN or OWNER to delete a Project via `deleteProject` mutation.
The system SHALL cascade-delete all related ProjectMemberships when a Project is deleted.

#### Scenario: Project deletion by Organization ADMIN

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `deleteProject` mutation을 호출하면
- **THEN** Project와 관련 ProjectMembership이 삭제된다
- **AND** 성공 응답이 반환된다

#### Scenario: Project deletion by MEMBER role

- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `deleteProject` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Project deletion by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `deleteProject` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Project deletion without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `deleteProject` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Project List Retrieval

The system SHALL allow Organization members to retrieve the list of Projects in an Organization via `projects(organizationId)` query.
The system SHALL filter the list so that Organization MEMBERs only see Projects they are assigned to, while ADMIN/OWNER see all Projects.

#### Scenario: Project list retrieval by Organization ADMIN

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `projects(organizationId)` query를 호출하면
- **THEN** 해당 Organization의 모든 프로젝트 목록이 반환된다

#### Scenario: Project list retrieval by Organization MEMBER

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `projects(organizationId)` query를 호출하면
- **THEN** 해당 사용자가 멤버로 할당된 프로젝트만 반환된다

#### Scenario: Project list retrieval by non-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `projects(organizationId)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Project list retrieval without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `projects(organizationId)` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Project Member Assignment

The system SHALL allow Organization ADMIN or OWNER to add an Organization member to a Project via `addProjectMember` mutation.
The system SHALL only allow adding users who are members of the parent Organization.
The system SHALL prevent duplicate ProjectMembership.

#### Scenario: Project member assignment success

- **GIVEN** Organization ADMIN 이상이 Organization 멤버인 유저를 프로젝트에 추가하려는 경우
- **WHEN** `addProjectMember` mutation을 호출하면
- **THEN** 해당 유저가 프로젝트 멤버로 추가된다
- **AND** 추가된 멤버 정보가 반환된다

#### Scenario: Project member assignment of non-organization-member

- **GIVEN** 대상 유저가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `addProjectMember` mutation을 호출하면
- **THEN** Organization 멤버가 아니라는 에러가 반환된다

#### Scenario: Project member assignment of already assigned member

- **GIVEN** 대상 유저가 이미 해당 프로젝트의 멤버인 경우
- **WHEN** `addProjectMember` mutation을 호출하면
- **THEN** 이미 프로젝트 멤버라는 에러가 반환된다

#### Scenario: Project member assignment by MEMBER role

- **GIVEN** Organization MEMBER 역할의 사용자가 멤버 추가를 시도하는 경우
- **WHEN** `addProjectMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Project member assignment without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `addProjectMember` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Project Member Removal

The system SHALL allow Organization ADMIN or OWNER to remove a member from a Project via `removeProjectMember` mutation.
The system SHALL delete the corresponding ProjectMembership record.

#### Scenario: Project member removal success

- **GIVEN** Organization ADMIN 이상이 프로젝트 멤버를 제거하려는 경우
- **WHEN** `removeProjectMember` mutation을 호출하면
- **THEN** 해당 유저의 ProjectMembership이 삭제된다
- **AND** 성공 응답이 반환된다

#### Scenario: Project member removal of non-project-member

- **GIVEN** 대상 유저가 해당 프로젝트의 멤버가 아닌 경우
- **WHEN** `removeProjectMember` mutation을 호출하면
- **THEN** 프로젝트 멤버가 아니라는 에러가 반환된다

#### Scenario: Project member removal by MEMBER role

- **GIVEN** Organization MEMBER 역할의 사용자가 멤버 제거를 시도하는 경우
- **WHEN** `removeProjectMember` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Project member removal without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `removeProjectMember` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다
