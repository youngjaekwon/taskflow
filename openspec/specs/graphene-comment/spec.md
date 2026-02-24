# graphene-comment Specification

## Purpose
TBD - created by archiving change add-graphene-comment. Update Purpose after archive.
## Requirements
### Requirement: Comment Creation
The system SHALL allow authenticated users with Task access to create a comment on a Task via `createComment` mutation.

#### Scenario: Comment creation success
- **GIVEN** 인증된 사용자가 해당 Task의 프로젝트 멤버이거나 Organization ADMIN 이상인 경우
- **WHEN** `createComment` mutation을 유효한 content와 taskId로 호출하면
- **THEN** 새 Comment가 해당 Task에 생성된다
- **AND** author가 현재 사용자로 설정된다
- **AND** 생성된 Comment 정보가 반환된다

#### Scenario: Reply creation success (1-depth)
- **GIVEN** 인증된 사용자가 Task 접근 권한을 가진 경우
- **WHEN** `createComment` mutation을 유효한 content, taskId, parentId로 호출하면
- **AND** parentId가 최상위 댓글(parent=null)인 경우
- **THEN** 대댓글이 생성되고 parent가 올바르게 설정된다

#### Scenario: Reply to reply rejected (depth limit)
- **GIVEN** parentId가 이미 대댓글(parent가 있는 댓글)인 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** depth 제한 에러가 반환된다

#### Scenario: Reply with non-existent parentId
- **GIVEN** 존재하지 않는 Comment ID가 parentId로 제공된 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** 부모 댓글 없음 에러가 반환된다

#### Scenario: Reply with parentId from different task
- **GIVEN** 다른 Task에 속한 댓글의 ID가 parentId로 제공된 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** 부모 댓글이 같은 Task에 속하지 않는다는 에러가 반환된다

#### Scenario: Comment creation with empty content
- **GIVEN** 빈 문자열이 content로 제공된 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Comment creation on non-existent task
- **GIVEN** 존재하지 않는 taskId가 제공된 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** Task 없음 에러가 반환된다

#### Scenario: Comment creation without task access
- **GIVEN** 인증된 사용자가 해당 Task의 프로젝트 멤버가 아니고 Organization ADMIN 이상도 아닌 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Comment creation without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createComment` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Comment Update
The system SHALL allow the comment author to update their own comment via `updateComment` mutation.

#### Scenario: Comment update success
- **GIVEN** 인증된 사용자가 해당 댓글의 작성자인 경우
- **WHEN** `updateComment` mutation을 새 content로 호출하면
- **THEN** 댓글 내용이 업데이트되고 갱신된 정보가 반환된다
- **AND** updatedAt이 갱신된다

#### Scenario: Comment update by non-author
- **GIVEN** 인증된 사용자가 해당 댓글의 작성자가 아닌 경우 (Org ADMIN 포함)
- **WHEN** `updateComment` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Comment update on non-existent comment
- **GIVEN** 존재하지 않는 Comment ID가 제공된 경우
- **WHEN** `updateComment` mutation을 호출하면
- **THEN** Comment 없음 에러가 반환된다

#### Scenario: Comment update with empty content
- **GIVEN** 빈 문자열이 content로 제공된 경우
- **WHEN** `updateComment` mutation을 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Comment update without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateComment` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Comment Deletion
The system SHALL allow the comment author to delete their own comment via `deleteComment` mutation.

#### Scenario: Comment deletion success
- **GIVEN** 인증된 사용자가 해당 댓글의 작성자인 경우
- **WHEN** `deleteComment` mutation을 호출하면
- **THEN** 댓글이 삭제되고 성공 응답이 반환된다

#### Scenario: Parent comment deletion with replies
- **GIVEN** 대댓글이 있는 부모 댓글을 삭제하는 경우
- **WHEN** `deleteComment` mutation을 호출하면
- **THEN** 부모 댓글이 삭제된다
- **AND** 해당 부모의 대댓글도 함께 CASCADE 삭제된다

#### Scenario: Comment deletion by non-author
- **GIVEN** 인증된 사용자가 해당 댓글의 작성자가 아닌 경우 (Org ADMIN 포함)
- **WHEN** `deleteComment` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Comment deletion without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `deleteComment` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Comment List Retrieval
The system SHALL allow users with Task access to retrieve a paginated list of comments for a Task via `comments` query.

#### Scenario: Comment list retrieval success
- **GIVEN** 인증된 사용자가 해당 Task의 프로젝트 멤버이거나 Organization ADMIN 이상인 경우
- **WHEN** `comments(taskId)` query를 호출하면
- **THEN** 해당 Task의 최상위 댓글(parent=null) 목록이 created_at 오름차순으로 반환된다
- **AND** 각 댓글에 replies 필드로 대댓글이 포함된다
- **AND** totalCount, hasNext, hasPrevious 페이지네이션 정보가 반환된다

#### Scenario: Comment list with pagination
- **GIVEN** Task에 댓글이 다수 존재하는 경우
- **WHEN** `comments(taskId, pagination: {limit, offset})` query를 호출하면
- **THEN** 지정된 limit/offset에 맞는 최상위 댓글이 반환된다
- **AND** hasNext, hasPrevious가 올바르게 설정된다

#### Scenario: Comment list retrieval without task access
- **GIVEN** 인증된 사용자가 해당 Task 접근 권한이 없는 경우
- **WHEN** `comments(taskId)` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Comment list retrieval without authentication
- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `comments(taskId)` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Comment Count on Task
The system SHALL expose a `commentCount` field on `TaskType` that returns the total number of comments for the Task.

#### Scenario: Comment count retrieval
- **GIVEN** Task에 댓글이 존재하는 경우
- **WHEN** Task 조회 시 `commentCount` 필드를 요청하면
- **THEN** 해당 Task의 전체 댓글 수(대댓글 포함)가 반환된다

#### Scenario: Comment count for task with no comments
- **GIVEN** Task에 댓글이 없는 경우
- **WHEN** Task 조회 시 `commentCount` 필드를 요청하면
- **THEN** 0이 반환된다

