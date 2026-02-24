# graphene-board Specification

## Purpose
TBD - created by archiving change add-graphene-board-taskgroup. Update Purpose after archive.
## Requirements
### Requirement: Board Creation
The system SHALL allow Organization ADMIN or OWNER to create a new Board under a Project via `createBoard` mutation.
The system SHALL auto-generate a unique slug from the Board name within the Project scope.
The system SHALL record the creator as `created_by`.

#### Scenario: Board creation success
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createBoard` mutation을 유효한 Board 이름과 Project ID로 호출하면
- **THEN** 새 Board가 해당 Project 하위에 생성된다
- **AND** 이름 기반으로 slug가 자동 생성된다
- **AND** 생성자가 `created_by`에 기록된다
- **AND** 생성된 Board 정보가 반환된다

#### Scenario: Board creation with duplicate slug in same project
- **GIVEN** 동일한 Project 내에서 같은 이름에서 파생된 slug가 이미 존재하는 경우
- **WHEN** `createBoard` mutation을 호출하면
- **THEN** slug에 숫자 접미사가 추가되어 Project 내 유일성이 보장된다

#### Scenario: Board creation by MEMBER role
- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `createBoard` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Board creation by non-organization-member
- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `createBoard` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Board creation without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createBoard` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

#### Scenario: Board creation with empty name
- **GIVEN** 빈 문자열이 Board 이름으로 제공된 경우
- **WHEN** `createBoard` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

---

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

### Requirement: Board Update
The system SHALL allow Organization ADMIN or OWNER to update Board information (name, description) via `updateBoard` mutation.
The system SHALL regenerate slug when name is changed.

#### Scenario: Board update success
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateBoard` mutation을 호출하면
- **THEN** Board 정보가 업데이트되고 갱신된 정보가 반환된다

#### Scenario: Board update by MEMBER role
- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `updateBoard` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Board update without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateBoard` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Board Deletion
The system SHALL allow Organization ADMIN or OWNER to delete a Board via `deleteBoard` mutation.
The system SHALL cascade-delete all associated TaskGroups when a Board is deleted.

#### Scenario: Board deletion by Organization ADMIN
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `deleteBoard` mutation을 호출하면
- **THEN** Board와 관련 TaskGroup이 모두 삭제된다
- **AND** 성공 응답이 반환된다

#### Scenario: Board deletion by MEMBER role
- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `deleteBoard` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Board deletion by non-organization-member
- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `deleteBoard` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Board deletion without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `deleteBoard` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: TaskGroup Creation
The system SHALL allow Organization ADMIN or OWNER to create a new TaskGroup under a Board via `createTaskGroup` mutation.
The system SHALL auto-assign position as `max(position) + 1` within the Board, placing new TaskGroup at the end.

#### Scenario: TaskGroup creation success
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createTaskGroup` mutation을 유효한 TaskGroup 이름과 Board ID로 호출하면
- **THEN** 새 TaskGroup이 해당 Board 하위에 생성된다
- **AND** position이 Board 내 마지막 위치로 자동 할당된다
- **AND** 생성된 TaskGroup 정보가 반환된다

#### Scenario: TaskGroup creation on empty board
- **GIVEN** Board에 TaskGroup이 하나도 없는 경우
- **WHEN** `createTaskGroup` mutation을 호출하면
- **THEN** position이 0으로 할당된다

#### Scenario: TaskGroup creation by MEMBER role
- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `createTaskGroup` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: TaskGroup creation without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createTaskGroup` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

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

### Requirement: TaskGroup Reordering
The system SHALL allow Organization ADMIN or OWNER to reorder TaskGroups within a Board via `reorderTaskGroups` mutation.
The system SHALL accept an ordered list of all TaskGroup IDs in the Board and reassign positions starting from 0.
The system SHALL validate that all provided IDs belong to the specified Board and that the list is complete.

#### Scenario: TaskGroup reordering success
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `reorderTaskGroups` mutation을 Board의 모든 TaskGroup ID를 원하는 순서로 호출하면
- **THEN** TaskGroup들의 position이 전달된 순서대로 0부터 재할당된다
- **AND** 갱신된 TaskGroup 목록이 반환된다

#### Scenario: TaskGroup reordering with incomplete list
- **GIVEN** 전달된 TaskGroup ID 목록이 Board의 전체 TaskGroup을 포함하지 않는 경우
- **WHEN** `reorderTaskGroups` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: TaskGroup reordering with invalid ID
- **GIVEN** 전달된 TaskGroup ID 중 해당 Board에 속하지 않는 ID가 포함된 경우
- **WHEN** `reorderTaskGroups` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: TaskGroup reordering by MEMBER role
- **GIVEN** 인증된 사용자가 Organization MEMBER 역할인 경우
- **WHEN** `reorderTaskGroups` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

---

### Requirement: Default Board and TaskGroup Auto-Creation
The system SHALL automatically create a default Board and TaskGroups when a new Project is created.
The default Board SHALL be named "Main Board".
The default TaskGroups SHALL be: "To Do" (position 0), "In Progress" (position 1), "In Review" (position 2), "Done" (position 3).
The system SHALL use Django `post_save` signal on Project model to trigger auto-creation.

#### Scenario: Default Board auto-creation on project creation
- **GIVEN** 새 Project가 생성된 경우
- **WHEN** Project 저장이 완료되면
- **THEN** "Main Board" 이름의 기본 Board가 자동 생성된다
- **AND** Board의 `created_by`는 Project의 `created_by`와 동일하게 설정된다
- **AND** 4개의 기본 TaskGroup이 position 순서대로 생성된다: "To Do"(0), "In Progress"(1), "In Review"(2), "Done"(3)

#### Scenario: No auto-creation on project update
- **GIVEN** 기존 Project가 수정된 경우
- **WHEN** Project 저장이 완료되면
- **THEN** 추가 Board나 TaskGroup이 생성되지 않는다

