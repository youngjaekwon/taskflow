## Context

Organization 서비스가 구현된 상태에서, Organization 하위 리소스인 Project를 추가한다. Project는 Organization 멤버 중 선택적으로 할당된 멤버만 접근할 수 있는 하위 단위이며, 향후 Board와 Task의 상위 컨테이너 역할을 한다.

## Goals / Non-Goals

- **Goals**:
  - Project CRUD (생성, 조회, 수정, 삭제)
  - Organization별 프로젝트 목록 조회
  - 프로젝트 멤버 할당/제거
  - Organization 역할 + ProjectMembership 기반 이중 접근 제어
- **Non-Goals**:
  - Board/TaskGroup 자동 생성 (별도 change에서 구현)
  - 프로젝트 아카이브 (P2 범위)
  - 프로젝트 자체 역할 시스템 (Organization 역할을 재사용)

## Decisions

### 1. 권한 모델: Organization 역할 재사용 + ProjectMembership 접근 제어

- **결정**: 프로젝트 자체 역할(project admin/member 등)을 도입하지 않고, Organization 역할 계층을 그대로 사용한다. ProjectMembership은 순수 접근 제어(프로젝트에 접근 가능한가?)만 담당한다.
- **근거**: features.md에 프로젝트별 역할 언급이 없으며, Organization 역할로 충분히 커버된다. 불필요한 복잡성을 피한다.
- **대안**: 프로젝트별 역할 도입 → 과도한 설계, 현재 요구사항에 불필요

### 2. 접근 제어 규칙

| 작업 | 권한 |
|------|------|
| 프로젝트 생성 | Organization ADMIN 이상 |
| 프로젝트 목록 조회 | Organization 멤버 (MEMBER는 할당된 프로젝트만, ADMIN+는 전체) |
| 프로젝트 상세 조회 | 프로젝트 멤버 또는 Organization ADMIN 이상 |
| 프로젝트 수정 | Organization ADMIN 이상 |
| 프로젝트 삭제 | Organization ADMIN 이상 |
| 멤버 할당/제거 | Organization ADMIN 이상 |

- **근거**: OWNER/ADMIN은 조직 관리자로서 모든 프로젝트에 접근해야 한다. MEMBER는 할당된 프로젝트만 접근하여 features.md P0 인가 #3을 충족한다.

### 3. Slug 유일성: Organization 범위 내 유일

- **결정**: `(organization, slug)` unique_together 사용. 글로벌 유일이 아닌 Organization 내 유일.
- **근거**: 다른 Organization에서 동일한 프로젝트 이름을 사용할 수 있어야 한다.

### 4. 프로젝트 생성 시 자동 멤버 등록

- **결정**: 프로젝트 생성자를 자동으로 ProjectMembership에 추가한다.
- **근거**: 생성자가 자신의 프로젝트에 접근하지 못하는 상황을 방지한다.

### 5. 프로젝트 삭제 시 cascade 동작

- **결정**: 프로젝트 삭제 시 ProjectMembership도 cascade 삭제된다 (Django default).
- **근거**: Organization 삭제 패턴과 일관성 유지. 향후 Board/Task도 cascade 삭제 대상.

## Risks / Trade-offs

- **ADMIN이 모든 프로젝트를 볼 수 있음**: MEMBER 입장에서 프로젝트가 "비공개"라고 인식할 수 있지만, ADMIN은 관리 목적으로 접근 가능. 이는 일반적인 조직 관리 패턴과 일치.
- **프로젝트 멤버에게 별도 역할 없음**: 향후 프로젝트 레벨 권한 세분화가 필요하면 ProjectMembership에 role 필드를 추가해야 함. 현재는 YAGNI 원칙 적용.

## Open Questions

없음 — features.md P0 요구사항으로 충분히 명확함.
