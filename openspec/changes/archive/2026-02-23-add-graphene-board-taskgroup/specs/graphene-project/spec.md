## MODIFIED Requirements

### Requirement: Project Creation
The system SHALL allow Organization ADMIN or OWNER to create a new Project under an Organization via `createProject` mutation.
The system SHALL auto-generate a unique slug from the Project name within the Organization scope.
The system SHALL automatically add the creator as a ProjectMembership upon Project creation.
The system SHALL trigger auto-creation of a default Board with default TaskGroups upon Project creation (see `graphene-board` spec).

#### Scenario: Project creation success
- **GIVEN** 인증된 사용자가 해당 Organization의 ADMIN 이상 역할인 경우
- **WHEN** `createProject` mutation을 유효한 프로젝트 이름과 Organization ID로 호출하면
- **THEN** 새 Project가 해당 Organization 하위에 생성된다
- **AND** 이름 기반으로 slug가 자동 생성된다
- **AND** 생성자가 ProjectMembership에 자동 추가된다
- **AND** 기본 Board와 TaskGroup이 자동 생성된다
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
