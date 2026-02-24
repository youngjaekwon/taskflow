## ADDED Requirements

### Requirement: Task Creation

The system SHALL allow authenticated users with project access to create a Task within a TaskGroup.
The system SHALL require a title (max 200 characters) for Task creation.
The system SHALL accept optional description, status, priority, assignee, and due_date fields.
The system SHALL default status to `todo` and priority to `medium` when not specified.
The system SHALL assign the Task a position at the end of the TaskGroup (max position + 1).
The system SHALL validate that the assignee is a member of the Project.
The system SHALL record the authenticated user as the Task creator (created_by).

#### Scenario: Task 생성 성공

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할이거나 Project 멤버인 경우
- **WHEN** `createTask` mutation을 유효한 TaskGroup ID와 제목으로 호출하면
- **THEN** 새 Task가 해당 TaskGroup 하위에 생성된다
- **AND** status는 `todo`, priority는 `medium`으로 기본 설정된다
- **AND** position은 해당 TaskGroup 내 마지막 위치로 자동 할당된다

#### Scenario: Task 생성 시 담당자 지정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `createTask` mutation에 assignee_id를 함께 전달하면
- **THEN** 해당 사용자가 Task 담당자로 지정된다

#### Scenario: Task 생성 시 Project 비멤버를 담당자로 지정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `createTask` mutation에 Project 멤버가 아닌 사용자를 assignee_id로 전달하면
- **THEN** 에러가 반환된다

#### Scenario: Task 생성 시 제목 미입력

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `createTask` mutation에 빈 제목을 전달하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Task 생성 권한 없음 (Organization 비소속)

- **GIVEN** 인증된 사용자가 해당 Organization에 소속되지 않은 경우
- **WHEN** `createTask` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Task 생성 미인증

- **GIVEN** 인증되지 않은 사용자인 경우
- **WHEN** `createTask` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

### Requirement: Task Update

The system SHALL allow authenticated users with project access to update a Task's title, description, status, priority, and due_date.
The system SHALL only update fields that are explicitly provided (partial update).
The system SHALL validate field values on update.

#### Scenario: Task 수정 성공

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `updateTask` mutation을 유효한 Task ID와 수정할 필드로 호출하면
- **THEN** 해당 필드만 업데이트된다
- **AND** 제공하지 않은 필드는 변경되지 않는다

#### Scenario: Task 상태 변경

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `updateTask` mutation으로 status를 `in_progress`로 변경하면
- **THEN** Task의 status가 `in_progress`로 업데이트된다

#### Scenario: Task 수정 권한 없음

- **GIVEN** 인증된 사용자가 해당 Organization에 소속되지 않은 경우
- **WHEN** `updateTask` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: 존재하지 않는 Task 수정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `updateTask` mutation을 존재하지 않는 Task ID로 호출하면
- **THEN** Task를 찾을 수 없다는 에러가 반환된다

### Requirement: Task Deletion

The system SHALL allow only the Task creator or Organization ADMIN/OWNER to delete a Task.
The system SHALL permanently delete the Task and adjust remaining positions in the TaskGroup.

#### Scenario: Task 삭제 성공 (생성자)

- **GIVEN** 인증된 사용자가 해당 Task의 생성자인 경우
- **WHEN** `deleteTask` mutation을 호출하면
- **THEN** Task가 삭제된다

#### Scenario: Task 삭제 성공 (Org ADMIN)

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `deleteTask` mutation을 호출하면
- **THEN** Task가 삭제된다

#### Scenario: Task 삭제 권한 없음 (Org MEMBER이면서 비생성자)

- **GIVEN** 인증된 사용자가 Organization MEMBER이면서 해당 Task의 생성자가 아닌 경우
- **WHEN** `deleteTask` mutation을 호출하면
- **THEN** 삭제 권한 에러가 반환된다

#### Scenario: Task 삭제 미인증

- **GIVEN** 인증되지 않은 사용자인 경우
- **WHEN** `deleteTask` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

### Requirement: Move Task to Different TaskGroup

The system SHALL allow authenticated users with project access to move a Task to a different TaskGroup within the same Board.
The system SHALL update the Task's task_group and position.
The system SHALL place the Task at a specified position or at the end of the target TaskGroup.

#### Scenario: Task를 다른 TaskGroup으로 이동

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `moveTask` mutation을 Task ID, 대상 TaskGroup ID, position으로 호출하면
- **THEN** Task가 대상 TaskGroup의 지정된 position으로 이동한다

#### Scenario: Task 이동 시 position 미지정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `moveTask` mutation을 position 없이 호출하면
- **THEN** Task가 대상 TaskGroup의 마지막 위치에 추가된다

#### Scenario: 다른 Board의 TaskGroup으로 이동 시도

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `moveTask` mutation으로 다른 Board의 TaskGroup으로 이동을 시도하면
- **THEN** 같은 Board 내에서만 이동 가능하다는 에러가 반환된다

### Requirement: Reorder Tasks Within TaskGroup

The system SHALL allow authenticated users with project access to reorder Tasks within the same TaskGroup.
The system SHALL accept a list of Task IDs representing the new order.
The system SHALL validate that all provided Task IDs belong to the specified TaskGroup.

#### Scenario: TaskGroup 내 Task 순서 변경

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `reorderTasks` mutation을 TaskGroup ID와 Task ID 목록으로 호출하면
- **THEN** 제공된 순서대로 Task의 position이 업데이트된다

#### Scenario: 다른 TaskGroup의 Task ID 포함 시

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `reorderTasks` mutation에 해당 TaskGroup에 속하지 않는 Task ID가 포함된 경우
- **THEN** 유효성 검증 에러가 반환된다

### Requirement: Task Assignment

The system SHALL allow authenticated users with project access to assign or change a Task's assignee.
The system SHALL validate that the assignee is a member of the Project.
The system SHALL allow clearing the assignee by passing null.

#### Scenario: Task 담당자 지정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `assignTask` mutation을 Task ID와 담당자 ID로 호출하면
- **THEN** 해당 사용자가 Task 담당자로 지정된다

#### Scenario: Task 담당자 해제

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `assignTask` mutation을 assignee_id를 null로 호출하면
- **THEN** Task의 담당자가 해제된다

#### Scenario: Project 비멤버를 담당자로 지정

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `assignTask` mutation에 Project 멤버가 아닌 사용자를 지정하면
- **THEN** 에러가 반환된다

### Requirement: Task Detail Query

The system SHALL allow authenticated users with project access to query a single Task by ID.
The system SHALL return all Task fields including assignee and task_group information.

#### Scenario: Task 상세 조회 성공

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `task` query를 유효한 Task ID로 호출하면
- **THEN** Task의 모든 필드(title, description, status, priority, assignee, due_date, task_group, position, created_by, created_at, updated_at)가 반환된다

#### Scenario: Task 상세 조회 권한 없음

- **GIVEN** 인증된 사용자가 해당 Organization에 소속되지 않은 경우
- **WHEN** `task` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: 존재하지 않는 Task 조회

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `task` query를 존재하지 않는 Task ID로 호출하면
- **THEN** Task를 찾을 수 없다는 에러가 반환된다

### Requirement: Task List Query with Filtering

The system SHALL allow authenticated users with project access to query a list of Tasks for a given Project.
The system SHALL support filtering by status (multiple), priority (multiple), assignee, due_date range, and keyword search (title, description icontains).
The system SHALL return Tasks ordered by task_group position, then by task position within each group by default.

#### Scenario: Project별 Task 목록 조회

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query를 Project ID로 호출하면
- **THEN** 해당 Project의 모든 Task가 반환된다

#### Scenario: 상태별 필터링

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 status 필터를 `[todo, in_progress]`로 지정하면
- **THEN** todo 또는 in_progress 상태인 Task만 반환된다

#### Scenario: 우선순위별 필터링

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 priority 필터를 `[high, urgent]`로 지정하면
- **THEN** high 또는 urgent 우선순위인 Task만 반환된다

#### Scenario: 담당자별 필터링

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 assignee_id 필터를 지정하면
- **THEN** 해당 담당자의 Task만 반환된다

#### Scenario: 기한 범위 필터링

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 due_date_from과 due_date_to를 지정하면
- **THEN** 해당 기간 내 기한인 Task만 반환된다

#### Scenario: 키워드 검색

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 search 키워드를 지정하면
- **THEN** 제목 또는 설명에 해당 키워드를 포함하는 Task만 반환된다

### Requirement: Task List Pagination

The system SHALL support offset-based pagination for Task list queries.
The system SHALL accept `limit` (default 20, max 100) and `offset` (default 0) parameters.
The system SHALL return a `TaskConnection` type containing `tasks`, `totalCount`, `hasNext`, and `hasPrevious` fields.

#### Scenario: 페이지네이션 적용

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 limit=10, offset=0으로 호출하면
- **THEN** 첫 10개의 Task와 totalCount, hasNext, hasPrevious가 반환된다

#### Scenario: 다음 페이지 조회

- **GIVEN** 총 25개의 Task가 있는 경우
- **WHEN** `tasks` query에 limit=10, offset=10으로 호출하면
- **THEN** 11~20번째 Task가 반환되고 hasNext=true, hasPrevious=true이다

#### Scenario: 기본 페이지네이션

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 pagination 파라미터 없이 호출하면
- **THEN** 기본값 limit=20, offset=0이 적용된다
