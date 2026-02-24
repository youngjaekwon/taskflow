## Context

features.md P1의 Comment 섹션(기능 #1~#4)을 backend-graphene에 구현한다. 기존 Task 모델 위에 Comment를 추가하며, TDD(RED-GREEN) 방식으로 개발한다.

## Goals / Non-Goals

- Goals:
  - Comment CRUD (생성, 수정, 삭제)
  - 대댓글 (1-depth 제한, parent FK)
  - Task별 댓글 목록 조회 + offset 기반 페이지네이션
  - 댓글 권한 (작성자만 수정/삭제 가능)
  - TaskType에 commentCount 필드 추가
- Non-Goals:
  - 무한 depth 대댓글 (1-depth 제한으로 충분)
  - 댓글 알림 (P2 실시간 알림에서 처리)
  - 댓글 멘션 (@user)
  - 댓글 리액션 (좋아요 등)

## Decisions

### Comment 모델 설계

```python
class Comment(models.Model):
    content    # TextField
    task       # FK → Task (CASCADE, related_name="comments")
    parent     # FK → self (CASCADE, null=True, blank=True, related_name="replies")
    author     # FK → CustomUser (SET_NULL, null=True, related_name="authored_comments")
    created_at # DateTimeField(auto_now_add)
    updated_at # DateTimeField(auto_now)

    class Meta:
        ordering = ["created_at"]
```

- **FK 삭제 정책**:
  - `task → CASCADE`: Task 삭제 시 댓글도 함께 삭제.
  - `parent → CASCADE`: 부모 댓글 삭제 시 대댓글도 함께 삭제. 1-depth 제한이므로 연쇄 깊이가 1로 제한되며, orphan 대댓글이 최상위로 승격되는 문제를 방지한다.
  - `author → SET_NULL`: 기존 코드베이스의 모든 User FK(`Task.created_by`, `Task.assignee`, `Board.created_by` 등)가 SET_NULL을 사용하므로 일관성 유지. 탈퇴한 사용자의 댓글은 author=null로 보존된다.
- **대안 검토**: Author CASCADE도 가능하나, 사용자 삭제 시 댓글이 대량 삭제되어 대화 맥락이 소실될 수 있고 기존 패턴과 불일치한다. Parent SET_NULL도 가능하나, orphan 대댓글이 최상위 목록에 노출되어 페이지네이션과 UI가 어긋날 수 있다.

### 대댓글 depth 제한

- 1-depth 제한: parent가 None인 댓글에만 대댓글 허용. parent가 있는 댓글에 대댓글 시도 시 에러.
- **대안 검토**: 무한 depth는 재귀 쿼리/직렬화 복잡성을 초래하며, 태스크 관리 도구에서 1-depth면 충분하다.

### 쿼리 설계

- `comments(taskId, pagination)`: Task에 속한 최상위 댓글(parent=null) 목록 반환. 각 댓글에 replies 필드로 대댓글 포함.
- 최상위 댓글만 페이지네이션 적용, 대댓글은 부모 댓글에 전부 포함.
- **대안 검토**: 대댓글도 별도 페이지네이션할 수 있으나, 1-depth 제한이므로 대댓글 수가 관리 가능한 범위이다.

### 권한 모델

- 댓글 조회/생성: Task 접근 권한과 동일 (Org ADMIN+ 또는 Project 멤버)
- 댓글 수정/삭제: 작성자(author)만 가능 → 별도 체크 로직 (Org ADMIN도 삭제 불가)
- **대안 검토**: Org ADMIN에게 삭제 권한을 부여할 수도 있으나, features.md에 "작성자만 수정/삭제 가능"으로 명시.

### PaginationInput 재사용

`PaginationInput`은 이미 `tasks/types.py`에 정의되어 있다. Graphene은 같은 이름의 서로 다른 InputObjectType 클래스를 허용하지 않으므로, 중복 정의 대신 공용 모듈로 추출한다.

- `graphql_utils.py`에 `PaginationInput`을 이동하고, `tasks/types.py`와 `comments/types.py` 모두에서 import하여 사용한다.
- `CommentConnectionType`도 동일한 페이지네이션 응답 패턴(`totalCount`, `hasNext`, `hasPrevious`)을 따른다.

### GraphQL 스키마

```graphql
type CommentType {
  id: ID!
  content: String!
  task: TaskType!
  parent: CommentType
  author: UserType
  replies: [CommentType!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type CommentConnectionType {
  comments: [CommentType!]!
  totalCount: Int!
  hasNext: Boolean!
  hasPrevious: Boolean!
}

# Mutations
createComment(input: CreateCommentInput!): CommentType
updateComment(input: UpdateCommentInput!): CommentType
deleteComment(id: ID!): { success: Boolean! }

# Queries
comments(taskId: ID!, pagination: PaginationInput): CommentConnectionType
```

- `author`는 `UserType`(nullable)이다. 사용자 탈퇴 시 author가 null이 될 수 있다.

## Risks / Trade-offs

- 부모 댓글 삭제 시 대댓글 CASCADE 삭제: 대댓글 데이터가 소실되지만, 1-depth 제한이므로 영향 범위가 제한적이고, orphan 대댓글이 최상위 목록에 노출되는 문제를 원천 차단한다.
- N+1 쿼리: replies 조회 시 N+1 가능 → 현재 규모에서는 prefetch_related로 충분. 필요 시 DataLoader 추가.
- commentCount N+1: Task 목록 조회 시 각 Task의 댓글 수 조회로 N+1 발생 가능 → `annotate(comment_count=Count("comments"))` 또는 DataLoader로 해결.

## Open Questions

- 없음
