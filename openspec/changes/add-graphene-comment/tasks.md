## 0. 앱 스캐폴딩

- [ ] 0.1 `comments` Django 앱 생성 (`python manage.py startapp comments`)
- [ ] 0.2 `config/settings/base.py`의 `INSTALLED_APPS`에 `comments` 추가
- [ ] 0.3 `comments/tests/` 디렉터리 구조 생성 (`__init__.py`, `conftest.py`, `factories.py`)

## 1. Comment 모델 (RED → GREEN)

- [ ] 1.1 `CommentFactory` 작성 (`comments/tests/factories.py`)
- [ ] 1.2 모델 테스트 작성 (`comments/tests/test_models.py`) — 필드 기본값, FK 관계, task CASCADE 삭제, parent CASCADE 삭제, author SET_NULL, ordering, `__str__`
- [ ] 1.3 `Comment` 모델 구현 (`comments/models.py`)
- [ ] 1.4 마이그레이션 생성 및 적용
- [ ] 1.5 테스트 통과 확인

## 2. PaginationInput 공용화

- [ ] 2.1 `tasks/types.py`의 `PaginationInput`을 `graphql_utils.py`로 이동
- [ ] 2.2 `tasks/types.py`에서 `graphql_utils.PaginationInput`을 import하도록 변경
- [ ] 2.3 기존 테스트 통과 확인 (tasks 앱 테스트)

## 3. GraphQL 타입 및 데코레이터

- [ ] 3.1 `CommentType` 정의 (`comments/types.py`) — 명시적 필드 화이트리스트, replies resolver
- [ ] 3.2 Input 타입 정의 — `CreateCommentInput`, `UpdateCommentInput`
- [ ] 3.3 `CommentConnectionType` 정의 (comments, totalCount, hasNext, hasPrevious)
- [ ] 3.4 `comments/decorators.py` — 댓글 접근 권한 데코레이터 (`comment_task_access_required`, `comment_author_required`). 기존 `tasks/decorators.py`의 `_check_project_access` 헬퍼 재사용

## 4. createComment 뮤테이션 (RED → GREEN)

- [ ] 4.1 테스트 작성 (`comments/tests/test_mutations.py: TestCreateComment`) — 성공, 대댓글 성공, 대대댓글 거부, 존재하지 않는 parentId, 다른 Task의 parentId, 빈 content, 존재하지 않는 Task, 권한 없음, 미인증
- [ ] 4.2 `CreateComment` 뮤테이션 구현 (`comments/mutations.py`)
- [ ] 4.3 테스트 통과 확인

## 5. updateComment 뮤테이션 (RED → GREEN)

- [ ] 5.1 테스트 작성 (`comments/tests/test_mutations.py: TestUpdateComment`) — 성공, 존재하지 않는 Comment ID, 비작성자 거부 (ADMIN 포함), 빈 content, 미인증
- [ ] 5.2 `UpdateComment` 뮤테이션 구현 (`comments/mutations.py`)
- [ ] 5.3 테스트 통과 확인

## 6. deleteComment 뮤테이션 (RED → GREEN)

- [ ] 6.1 테스트 작성 (`comments/tests/test_mutations.py: TestDeleteComment`) — 성공, 대댓글 있는 부모 삭제 시 대댓글 CASCADE 삭제, 비작성자 거부, 미인증
- [ ] 6.2 `DeleteComment` 뮤테이션 구현 (`comments/mutations.py`)
- [ ] 6.3 테스트 통과 확인

## 7. comments 목록 쿼리 + 페이지네이션 (RED → GREEN)

- [ ] 7.1 테스트 작성 (`comments/tests/test_queries.py: TestCommentList`) — 목록 조회 (최상위 댓글만 + replies 포함), created_at 정렬 (최상위 + 대댓글 모두), 권한 없음, 미인증
- [ ] 7.2 테스트 작성 (`comments/tests/test_queries.py: TestCommentPagination`) — 페이지네이션 기본, 다음 페이지, 기본값 적용
- [ ] 7.3 `CommentQuery` 구현 (`comments/queries.py`) — `comments(taskId, pagination)` resolver
- [ ] 7.4 테스트 통과 확인

## 8. TaskType commentCount 필드 (RED → GREEN)

- [ ] 8.1 테스트 작성 (`comments/tests/test_queries.py: TestCommentCount`) — Task 조회 시 commentCount 반환, 댓글 없는 Task는 0
- [ ] 8.2 `tasks/types.py`의 `TaskType`에 `comment_count` 필드 및 resolver 추가
- [ ] 8.3 테스트 통과 확인

## 9. 스키마 통합 및 최종 검증

- [ ] 9.1 `comments/schema.py` 작성 — CommentQuery, CommentMutation 조합
- [ ] 9.2 `config/schema.py`에 CommentQuery, CommentMutation 통합
- [ ] 9.3 전체 테스트 실행 (`pytest`) — 기존 테스트 포함 모두 통과 확인
- [ ] 9.4 린트 실행 (`ruff check`, `ruff format`) — All checks passed
