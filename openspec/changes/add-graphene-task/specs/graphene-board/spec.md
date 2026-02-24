## MODIFIED Requirements

### Requirement: Board Retrieval

The system SHALL allow project members and Organization ADMIN/OWNER to view Board details via `board(id)` query.
The system SHALL return Board details including associated TaskGroups sorted by position.
The system SHALL allow project members and Organization ADMIN/OWNER to list all Boards in a Project via `boards(projectId)` query.
The system SHALL expose a `tasks` field on TaskGroupType that returns the ordered list of Tasks (by position ascending) within the TaskGroup.

#### Scenario: Board detail retrieval by project member

- **GIVEN** 인증된 사용자가 해당 프로젝트의 멤버인 경우
- **WHEN** `board(id)` query를 호출하면
- **THEN** Board 상세 정보(id, name, slug, description, project, taskGroups, createdBy, timestamps)가 반환된다
- **AND** taskGroups는 position 오름차순으로 정렬되어 반환된다

#### Scenario: TaskGroup의 tasks 필드 조회

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** Board 쿼리에서 TaskGroup의 tasks 필드를 요청하면
- **THEN** 해당 TaskGroup에 속한 Task 목록이 position 오름차순으로 반환된다

#### Scenario: Board detail retrieval by Organization ADMIN

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상이지만 프로젝트 멤버가 아닌 경우
- **WHEN** `board(id)` query를 호출하면
- **THEN** Board 상세 정보가 반환된다

#### Scenario: Board detail retrieval by non-project-member MEMBER

- **GIVEN** 인증된 사용자가 Organization MEMBER이지만 해당 프로젝트의 멤버가 아닌 경우
- **WHEN** `board(id)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Board list retrieval by project member

- **GIVEN** 인증된 사용자가 해당 프로젝트의 멤버인 경우
- **WHEN** `boards(projectId)` query를 호출하면
- **THEN** 해당 Project의 모든 Board 목록이 반환된다

#### Scenario: Board list retrieval by non-organization-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `boards(projectId)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Board retrieval without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `board(id)` 또는 `boards(projectId)` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

### Requirement: TaskGroup Update and Deletion

The system SHALL allow Organization ADMIN or OWNER to update TaskGroup name via `updateTaskGroup` mutation.
The system SHALL allow Organization ADMIN or OWNER to delete a TaskGroup via `deleteTaskGroup` mutation.
The system SHALL prevent deletion of a TaskGroup that contains Tasks; the user MUST move or delete all Tasks first.

#### Scenario: TaskGroup update success

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateTaskGroup` mutation을 호출하면
- **THEN** TaskGroup 이름이 업데이트되고 갱신된 정보가 반환된다

#### Scenario: TaskGroup update by MEMBER role

- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `updateTaskGroup` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: TaskGroup deletion success

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할이고, TaskGroup에 Task가 없는 경우
- **WHEN** `deleteTaskGroup` mutation을 호출하면
- **THEN** TaskGroup이 삭제된다
- **AND** 성공 응답이 반환된다

#### Scenario: TaskGroup deletion blocked by existing Tasks

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할이고, TaskGroup에 Task가 존재하는 경우
- **WHEN** `deleteTaskGroup` mutation을 호출하면
- **THEN** Task가 존재하여 삭제할 수 없다는 에러가 반환된다

#### Scenario: TaskGroup deletion by MEMBER role

- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `deleteTaskGroup` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: TaskGroup deletion without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateTaskGroup` 또는 `deleteTaskGroup` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다
