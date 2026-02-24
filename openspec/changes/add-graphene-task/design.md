## Context

features.md의 P0 Task 섹션(기능 #1~#9)을 backend-graphene에 구현한다. 기존 Board/TaskGroup 구조 위에 Task를 추가하며, TDD(RED-GREEN) 방식으로 개발한다.

## Goals / Non-Goals

- Goals:
  - Task CRUD (생성, 수정, 삭제)
  - Task 상태 관리 (todo/in_progress/in_review/done)
  - Task를 다른 TaskGroup으로 이동 (moveTask)
  - 같은 TaskGroup 내 Task 순서 변경 (reorderTasks)
  - Task 담당자 지정/변경 (assignTask)
  - Task 목록 복합 필터링 (상태, 우선순위, 담당자, 기한 범위, 키워드)
  - Task 목록 offset 기반 페이지네이션
  - Task 삭제 권한 (생성자 또는 Org ADMIN+)
- Non-Goals:
  - Comment, Label, 파일 첨부 (P1 별도 변경)
  - 실시간 알림, Activity Log (P1/P2 별도 변경)
  - Cursor 기반 페이지네이션 (향후 필요 시 추가)

## Decisions

### Task 모델 설계

```python
class TaskStatus(models.TextChoices):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"

class TaskPriority(models.TextChoices):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(models.Model):
    title         # CharField(max_length=200)
    description   # TextField(blank=True, default="")
    status        # CharField(choices=TaskStatus, default=TODO)
    priority      # CharField(choices=TaskPriority, default=MEDIUM)
    task_group    # FK → TaskGroup (CASCADE → tasks)
    position      # PositiveIntegerField(default=0)
    assignee      # FK → CustomUser (SET_NULL, null=True, blank=True)
    due_date      # DateField(null=True, blank=True)
    created_by    # FK → CustomUser (SET_NULL)
    created_at    # DateTimeField(auto_now_add)
    updated_at    # DateTimeField(auto_now)
```

- **대안 검토**: Task에 project FK를 추가할 수도 있으나, task_group → board → project 경로로 충분히 추적 가능하므로 중복 FK를 두지 않는다.

### 페이지네이션

- Offset 기반 (limit/offset) 선택. totalCount를 함께 반환한다.
- **대안 검토**: Cursor 기반은 실시간 데이터에 유리하나, 현재 규모에서는 과도한 복잡성이다.

### 권한 모델

- Task 조회/생성/수정: 기존 `project_access_required` 패턴 재사용 (Org ADMIN+ 또는 Project 멤버)
- Task 삭제: 생성자(created_by) 또는 Org ADMIN 이상만 가능 → 별도 데코레이터 `task_delete_permission_required`
- Task 담당자 지정: Project 멤버만 담당자로 지정 가능

### 필터링

- 쿼리 파라미터로 필터 Input 타입 사용:
  - status: [TaskStatus] (복수 선택)
  - priority: [TaskPriority] (복수 선택)
  - assignee_id: ID (단일)
  - due_date_from / due_date_to: Date (범위)
  - search: String (title, description 키워드 검색, icontains)

## Risks / Trade-offs

- Task position 관리: TaskGroup 내 position 갱신 시 동시성 이슈 가능 → ATOMIC_MUTATIONS=True로 트랜잭션 보호
- 필터링 성능: 대규모 데이터 시 인덱스 필요 → 현재 규모에서는 불필요, 필요 시 추가

## Open Questions

- 없음
