## 1. 부트스트랩

- [ ] 1.1 `projects` Django 앱 생성 및 `INSTALLED_APPS` 등록
- [ ] 1.2 빈 모델 스텁 작성 (`Project`, `ProjectMembership` — 최소 필드만, FK 포함)
- [ ] 1.3 초기 마이그레이션 생성 및 적용
- [ ] 1.4 팩토리 작성 (`ProjectFactory`, `ProjectMembershipFactory`)
- [ ] 1.5 `conftest.py`에 프로젝트 관련 픽스처 추가

## 2. 모델 TDD

- [ ] 2.1 **RED**: 모델 테스트 작성 (slug 자동 생성, Organization 범위 내 slug 유일성, unique_together, cascade 삭제)
- [ ] 2.2 **GREEN**: `Project` 모델 구현 (name, slug, description, organization FK, created_by FK, timestamps)
- [ ] 2.3 **GREEN**: `ProjectMembership` through 모델 구현 (project FK, user FK, added_by FK, joined_at, unique_together)
- [ ] 2.4 **GREEN**: slug 자동 생성 로직 구현 (Organization 범위 내 유일성, 중복 시 숫자 접미사)
- [ ] 2.5 마이그레이션 업데이트 및 적용

## 3. GraphQL 타입 / 데코레이터

- [ ] 3.1 `ProjectType` (DjangoObjectType) 정의 — 명시적 필드 화이트리스트
- [ ] 3.2 `ProjectMemberType` (DjangoObjectType) 정의
- [ ] 3.3 Input 타입 정의 (`CreateProjectInput`, `UpdateProjectInput`, `AddProjectMemberInput`, `RemoveProjectMemberInput`)
- [ ] 3.4 `project_access_required` 데코레이터 구현 — 프로젝트 멤버 또는 Organization ADMIN 이상만 접근 허용
- [ ] 3.5 기존 `org_role_required` 재사용하여 프로젝트 관리(생성/수정/삭제/멤버관리) 권한 처리
- [ ] 3.6 `projects/schema.py` 스텁 작성 (빈 Query/Mutation 클래스)

## 4. createProject TDD

- [ ] 4.1 **RED**: createProject 테스트 작성 (성공, 생성자 자동 멤버 등록, 권한 검증 — ADMIN 이상만)
- [ ] 4.2 **GREEN**: `createProject` mutation 구현

## 5. project 조회 TDD

- [ ] 5.1 **RED**: project(id) 조회 테스트 작성 (성공, 접근 제어 — 프로젝트 멤버 또는 ADMIN 이상)
- [ ] 5.2 **GREEN**: `project(id)` query 구현

## 6. projects 목록 TDD

- [ ] 6.1 **RED**: projects(organizationId) 목록 테스트 작성 (ADMIN은 전체, MEMBER는 할당된 프로젝트만)
- [ ] 6.2 **GREEN**: `projects(organizationId)` query 구현

## 7. updateProject TDD

- [ ] 7.1 **RED**: updateProject 테스트 작성 (부분 업데이트, 권한 검증 — ADMIN 이상만)
- [ ] 7.2 **GREEN**: `updateProject` mutation 구현

## 8. deleteProject TDD

- [ ] 8.1 **RED**: deleteProject 테스트 작성 (cascade 삭제, 권한 검증 — ADMIN 이상만)
- [ ] 8.2 **GREEN**: `deleteProject` mutation 구현

## 9. addProjectMember TDD

- [ ] 9.1 **RED**: addProjectMember 테스트 작성 (Organization 멤버 할당, 중복 방지, 권한 검증 — ADMIN 이상만)
- [ ] 9.2 **GREEN**: `addProjectMember` mutation 구현

## 10. removeProjectMember TDD

- [ ] 10.1 **RED**: removeProjectMember 테스트 작성 (멤버 제거, 비멤버 처리, 권한 검증 — ADMIN 이상만)
- [ ] 10.2 **GREEN**: `removeProjectMember` mutation 구현

## 11. 스키마 통합 + 전체 검증

- [ ] 11.1 `projects/schema.py`에서 ProjectQuery, ProjectMutation 조합
- [ ] 11.2 `config/schema.py` 루트 스키마에 통합
- [ ] 11.3 전체 테스트 실행 및 검증
