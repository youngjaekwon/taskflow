## MODIFIED Requirements

### Requirement: Task Detail Query

The system SHALL allow authenticated users with project access to query a single Task by ID.
The system SHALL return all Task fields including assignee, task_group, and labels information.

#### Scenario: Task 상세 조회 성공

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `task` query를 유효한 Task ID로 호출하면
- **THEN** Task의 모든 필드(title, description, status, priority, assignee, due_date, task_group, position, labels, created_by, created_at, updated_at)가 반환된다

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
The system SHALL support filtering by status (multiple), priority (multiple), assignee, due_date range, keyword search (title, description icontains), and label_ids (multiple, OR condition).
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

#### Scenario: Label 필터링

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `tasks` query에 label_ids 필터를 `[labelId1, labelId2]`로 지정하면
- **THEN** 지정된 Label 중 하나 이상이 할당된 Task만 반환된다 (OR 조건)
- **AND** 중복 없이 반환된다
