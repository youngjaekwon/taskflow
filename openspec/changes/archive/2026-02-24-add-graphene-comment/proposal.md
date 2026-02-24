# Change: Comment 서비스 추가 (backend-graphene)

## Why

Task에 대한 협업과 커뮤니케이션을 지원하기 위해 댓글(Comment) 기능이 필요하다. features.md P1에 정의된 Comment 요구사항(CRUD, 대댓글, 페이지네이션, 권한)을 backend-graphene에 TDD 방식으로 구현한다.

## What Changes

- **새 Django 앱**: `comments` 앱 생성 (Comment 모델, GraphQL 타입/쿼리/뮤테이션)
- **Comment 모델**: content, task(FK CASCADE), parent(self FK CASCADE, 1-depth 대댓글), author(FK SET_NULL), timestamps
- **GraphQL 뮤테이션**: `createComment`, `updateComment`, `deleteComment`
- **GraphQL 쿼리**: `comments` (Task별 댓글 목록 + 페이지네이션)
- **권한 제어**: 댓글 수정/삭제는 작성자만 가능, 댓글 조회/생성은 Task 접근 권한과 동일
- **TaskType 확장**: `commentCount` 필드 추가

## Impact

- Affected specs: `graphene-comment` (신규)
- Affected code: `apps/backend-graphene/comments/` (신규), `apps/backend-graphene/tasks/types.py` (commentCount 추가), `apps/backend-graphene/graphql_utils.py` (PaginationInput 이동), `apps/backend-graphene/config/schema.py`, `apps/backend-graphene/config/settings/base.py`
