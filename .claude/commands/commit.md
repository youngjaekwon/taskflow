모든 변경사항을 스테이징하고 커밋하라.

## 절차

1. `git status`와 `git diff`로 현재 변경사항을 확인한다
2. 변경사항이 없으면 "커밋할 변경사항이 없습니다"라고 알리고 종료한다
3. 스테이징 전 `.env`, `credentials`, `secret` 등 민감 파일이 변경사항에 포함되어 있는지 확인한다
4. 민감 파일이 있으면 사용자에게 경고하고 확인을 받는다
5. 모든 변경사항을 스테이징한다 (`git add -A`)
6. 아래 커밋 컨벤션에 따라 커밋 메시지를 작성한다
7. 커밋을 실행한다
8. 커밋 결과를 보여준다

## 커밋 컨벤션

Conventional Commits 형식을 따른다.

### 형식

```
<type>(<scope>): <subject>

<body>
```

### Type

| Type       | 설명                          |
| ---------- | ----------------------------- |
| `feat`     | 새로운 기능 추가              |
| `fix`      | 버그 수정                     |
| `refactor` | 리팩터링 (기능 변경 없음)     |
| `docs`     | 문서 변경                     |
| `style`    | 코드 포맷팅, 세미콜론 등      |
| `test`     | 테스트 추가/수정              |
| `chore`    | 빌드, 설정 등 기타 변경       |
| `ci`       | CI/CD 설정 변경               |
| `perf`     | 성능 개선                     |

### Scope

선택사항. 해당 앱/패키지명을 사용한다: `web`, `backend-graphene`, `backend-strawberry` 등.

### Subject (제목)

- **영어**로 작성
- 소문자로 시작, 마침표 없음
- 명령형(imperative) 사용 (예: "add" O, "added" X, "adds" X)

### Body (본문)

- **한국어**로 작성
- 변경 이유와 맥락을 설명

### 예시

```
feat(web): add task list component

태스크 목록을 표시하는 SvelteKit 컴포넌트 추가.
GraphQL 쿼리로 백엔드에서 태스크를 가져와 렌더링한다.
```

```
fix(backend-graphene): handle empty query result

빈 쿼리 결과에 대한 null 체크가 누락되어 500 에러가 발생하던 문제 수정.
```
