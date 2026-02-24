## Context

features.md P1 Label 섹션을 backend-graphene에 구현한다. Label은 Organization 레벨 리소스로, 해당 Organization 내 모든 Project의 Task에 할당할 수 있다. TDD(RED-GREEN-REFACTOR) 방식으로 개발한다.

## Goals / Non-Goals

- Goals:
  - Label CRUD (Organization 레벨)
  - Label 색상 코드 (hex 형식)
  - Task에 Label 추가/제거 (M2M)
  - Label 기반 Task 필터링
  - TDD 방식 개발
- Non-Goals:
  - Project 레벨 Label (Organization 레벨에서 공유)
  - Label 계층 구조 (flat 구조)
  - Label 아이콘/이모지 (색상만)

## Decisions

### Label 모델 설계

```python
class Label(models.Model):
    name         # CharField(max_length=50)
    color        # CharField(max_length=7, default="#808080") — hex color code
    organization # FK → Organization (CASCADE → labels)
    created_by   # FK → CustomUser (SET_NULL, null=True)
    created_at   # DateTimeField(auto_now_add)
    updated_at   # DateTimeField(auto_now)

    class Meta:
        unique_together = ("organization", "name")
```

- **Label 범위**: Organization 레벨. features.md에 "Organization 레벨에서 공유되는 Label 관리"로 명시.
- **대안 검토**: Project 레벨 Label도 고려했으나, Organization 내 일관된 분류 체계를 위해 Organization 레벨로 결정.

### Task-Label 관계

```python
# tasks/models.py — Task 모델에 추가
labels = models.ManyToManyField("labels.Label", blank=True, related_name="tasks")
```

- Django의 자동 생성 중간 테이블(`tasks_task_labels`) 사용. 별도 through 모델은 추가 메타데이터가 없으므로 불필요.

### 색상 코드 검증

- `#` 접두어 포함 7자리 hex 형식 (`#RRGGBB`) 검증
- Django 모델의 `clean_fields()` + `RegexValidator` 사용 (기존 프로젝트 패턴 준수)

### 권한 모델

- Label CRUD: Organization ADMIN 이상 (Organization 레벨 리소스이므로, Board/TaskGroup 패턴과 동일)
- Task-Label 관계 관리: Project 접근 권한 (기존 `task_access_required` 패턴 재사용)
- Label 목록 조회: Organization 멤버 (기존 org 멤버십 확인 패턴 재사용)

### GraphQL 스키마

```graphql
# Types
type LabelType {
  id: ID!
  name: String!
  color: String!
  organization: OrganizationType!
  createdBy: UserType
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Queries
labels(organizationId: ID!): [LabelType!]!

# Mutations
createLabel(input: CreateLabelInput!): CreateLabel
updateLabel(input: UpdateLabelInput!): UpdateLabel
deleteLabel(id: ID!): DeleteLabel
addLabelsToTask(input: AddLabelsToTaskInput!): AddLabelsToTask
removeLabelsFromTask(input: RemoveLabelsFromTaskInput!): RemoveLabelsFromTask
```

### Task 필터링 확장

```python
class TaskFilterInput(graphene.InputObjectType):
    # ... 기존 필터 ...
    label_ids = graphene.List(graphene.NonNull(graphene.ID))  # 추가
```

- label_ids 필터: 지정된 Label ID 목록 중 하나 이상을 가진 Task를 반환 (OR 조건)

## Risks / Trade-offs

- Task-Label M2M 조회 시 N+1 가능 → 현재 단계에서는 `prefetch_related`로 해결, 추후 DataLoader로 최적화 가능
- Label 삭제 시 관련 Task의 M2M 관계도 자동 정리됨 (Django CASCADE 기본 동작)

## Open Questions

- 없음
