## ADDED Requirements

### Requirement: Label Creation

The system SHALL allow Organization ADMIN or OWNER to create a Label within an Organization via `createLabel` mutation.
The system SHALL require a name (max 50 characters) and accept an optional color code (hex format `#RRGGBB`, default `#808080`).
The system SHALL enforce unique Label names within the same Organization.
The system SHALL validate the color code format.
The system SHALL record the authenticated user as the Label creator (created_by).

#### Scenario: Label 생성 성공

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createLabel` mutation을 유효한 Organization ID, 이름, 색상 코드로 호출하면
- **THEN** 새 Label이 해당 Organization 하위에 생성된다
- **AND** 생성자가 `created_by`에 기록된다
- **AND** 생성된 Label 정보가 반환된다

#### Scenario: Label 생성 시 색상 코드 미지정

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createLabel` mutation을 색상 코드 없이 호출하면
- **THEN** 기본 색상 `#808080`이 적용된다

#### Scenario: Label 생성 시 중복 이름

- **GIVEN** 동일한 Organization 내에 같은 이름의 Label이 이미 존재하는 경우
- **WHEN** `createLabel` mutation을 호출하면
- **THEN** 중복 이름 에러가 반환된다

#### Scenario: Label 생성 시 잘못된 색상 코드

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createLabel` mutation을 유효하지 않은 색상 코드(예: "red", "#GGG")로 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Label 생성 시 빈 이름

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createLabel` mutation을 빈 이름으로 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Label 생성 by MEMBER role

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `createLabel` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: Label 생성 by non-organization-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `createLabel` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Label 생성 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `createLabel` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Label Update

The system SHALL allow Organization ADMIN or OWNER to update a Label's name and/or color via `updateLabel` mutation.
The system SHALL only update fields that are explicitly provided (partial update).
The system SHALL enforce unique Label names within the same Organization on update.
The system SHALL validate the color code format on update.

#### Scenario: Label 수정 성공

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateLabel` mutation을 유효한 Label ID와 수정할 필드로 호출하면
- **THEN** 해당 필드만 업데이트된다
- **AND** 제공하지 않은 필드는 변경되지 않는다

#### Scenario: Label 이름 수정 시 중복

- **GIVEN** 동일한 Organization 내에 같은 이름의 다른 Label이 존재하는 경우
- **WHEN** `updateLabel` mutation으로 해당 이름으로 변경하면
- **THEN** 중복 이름 에러가 반환된다

#### Scenario: Label 수정 시 잘못된 색상 코드

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateLabel` mutation을 유효하지 않은 색상 코드로 호출하면
- **THEN** 유효성 검증 에러가 반환된다

#### Scenario: Label 수정 by MEMBER role

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `updateLabel` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: 존재하지 않는 Label 수정

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `updateLabel` mutation을 존재하지 않는 Label ID로 호출하면
- **THEN** Label을 찾을 수 없다는 에러가 반환된다

#### Scenario: Label 수정 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateLabel` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Label Deletion

The system SHALL allow Organization ADMIN or OWNER to delete a Label via `deleteLabel` mutation.
The system SHALL remove all Task-Label associations when a Label is deleted.

#### Scenario: Label 삭제 성공

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `deleteLabel` mutation을 유효한 Label ID로 호출하면
- **THEN** Label이 삭제된다
- **AND** 해당 Label과 연결된 모든 Task-Label 관계가 자동으로 제거된다

#### Scenario: Label 삭제 by MEMBER role

- **GIVEN** 인증된 사용자가 해당 Organization의 MEMBER 역할인 경우
- **WHEN** `deleteLabel` mutation을 호출하면
- **THEN** 권한 부족 에러가 반환된다

#### Scenario: 존재하지 않는 Label 삭제

- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `deleteLabel` mutation을 존재하지 않는 Label ID로 호출하면
- **THEN** Label을 찾을 수 없다는 에러가 반환된다

#### Scenario: Label 삭제 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `deleteLabel` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Label List Query

The system SHALL allow Organization members to query a list of Labels for a given Organization via `labels(organizationId)` query.
The system SHALL return Labels ordered by name alphabetically.

#### Scenario: Label 목록 조회 성공

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버인 경우
- **WHEN** `labels` query를 Organization ID로 호출하면
- **THEN** 해당 Organization의 모든 Label이 이름순으로 반환된다

#### Scenario: Label 목록 조회 by non-organization-member

- **GIVEN** 인증된 사용자가 해당 Organization의 멤버가 아닌 경우
- **WHEN** `labels` query를 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Label 목록 조회 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `labels` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Add Labels to Task

The system SHALL allow authenticated users with project access to add one or more Labels to a Task via `addLabelsToTask` mutation.
The system SHALL validate that the Labels belong to the same Organization as the Task's Project.
The system SHALL ignore Labels that are already assigned to the Task (idempotent).

#### Scenario: Task에 Label 추가 성공

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `addLabelsToTask` mutation을 Task ID와 Label ID 목록으로 호출하면
- **THEN** 해당 Label들이 Task에 추가된다
- **AND** 기존에 이미 할당된 Label은 중복 추가되지 않는다

#### Scenario: 다른 Organization의 Label 추가 시도

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `addLabelsToTask` mutation에 다른 Organization의 Label ID를 전달하면
- **THEN** 에러가 반환된다

#### Scenario: Task에 Label 추가 권한 없음

- **GIVEN** 인증된 사용자가 해당 Organization에 소속되지 않은 경우
- **WHEN** `addLabelsToTask` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Task에 Label 추가 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `addLabelsToTask` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Remove Labels from Task

The system SHALL allow authenticated users with project access to remove one or more Labels from a Task via `removeLabelsFromTask` mutation.
The system SHALL ignore Labels that are not currently assigned to the Task (idempotent).

#### Scenario: Task에서 Label 제거 성공

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `removeLabelsFromTask` mutation을 Task ID와 Label ID 목록으로 호출하면
- **THEN** 해당 Label들이 Task에서 제거된다

#### Scenario: 할당되지 않은 Label 제거 시도

- **GIVEN** 인증된 사용자가 프로젝트 접근 권한이 있는 경우
- **WHEN** `removeLabelsFromTask` mutation에 Task에 할당되지 않은 Label ID를 전달하면
- **THEN** 에러 없이 성공 응답이 반환된다

#### Scenario: Task에서 Label 제거 권한 없음

- **GIVEN** 인증된 사용자가 해당 Organization에 소속되지 않은 경우
- **WHEN** `removeLabelsFromTask` mutation을 호출하면
- **THEN** 접근 권한 에러가 반환된다

#### Scenario: Task에서 Label 제거 미인증

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `removeLabelsFromTask` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다
