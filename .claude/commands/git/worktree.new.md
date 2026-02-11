---
name: "Git: Worktree New"
description: "git worktree와 브랜치를 한 번에 생성"
category: "Git Workflow"
tags: [git, worktree]
---

## 입력

```
$ARGUMENTS
```

Conventional Commits 형식의 문자열을 받는다: `<type>(<scope>): <subject>` 또는 `<type>: <subject>`

## 절차

1. `$ARGUMENTS`가 비어있으면 아래 **사용법 안내**를 출력하고 종료한다
2. `$ARGUMENTS`를 파싱하여 type, scope(선택), subject를 추출한다
   - 정규식: `^(feat|fix|refactor|docs|style|test|chore|ci|perf)(\(([^)]+)\))?:\s*(.+)$`
   - 파싱 실패 시 올바른 형식을 안내하고 종료한다
3. subject를 kebab-case로 변환한다 (소문자화, 공백을 하이픈으로 치환)
4. 브랜치명과 워크트리 경로를 조합한다:

   | 항목          | scope 있음                          | scope 없음                  |
   | ------------- | ----------------------------------- | --------------------------- |
   | 브랜치명      | `<type>/<scope>/<subject-kebab>`    | `<type>/<subject-kebab>`    |
   | 워크트리 경로 | `../<type>-<scope>-<subject-kebab>` | `../<type>-<subject-kebab>` |

5. 동일 브랜치가 이미 존재하는지 `git branch --list <브랜치명>`으로 확인한다
   - 존재하면 "이미 존재하는 브랜치입니다: `<브랜치명>`"을 알리고 종료한다
6. 워크트리 경로가 이미 존재하는지 확인한다
   - 존재하면 "이미 존재하는 경로입니다: `<경로>`"를 알리고 종료한다
7. `git worktree add <워크트리 경로> -b <브랜치명>`을 실행한다
8. 생성 결과를 아래 형식으로 출력한다:

```
워크트리가 생성되었습니다.

- 브랜치: `<브랜치명>`
- 경로: `<워크트리 경로>`

해당 디렉터리로 이동하려면:
cd <워크트리 경로>
```

## 에러 처리

- `$ARGUMENTS`가 비어있거나 공백만 있으면 사용법을 안내한다
- type이 허용 목록에 없으면 올바른 type 목록을 안내한다
- 파싱 실패 시 올바른 형식 예시를 보여준다
- git worktree add 명령 실패 시 에러 메시지를 그대로 전달한다

## 사용법 안내

```
사용법: /git:worktree.new <type>(<scope>): <subject>

예시:
  /git:worktree.new feat(web): add task list component
  /git:worktree.new fix(backend-graphene): handle empty query
  /git:worktree.new chore: update dependencies

Type: feat, fix, refactor, docs, style, test, chore, ci, perf
Scope: 선택사항 (web, backend-graphene, backend-strawberry 등)
```

## 참조 컨벤션 (/git:commit과 동일)

### Type

| Type       | 설명                      |
| ---------- | ------------------------- |
| `feat`     | 새로운 기능 추가          |
| `fix`      | 버그 수정                 |
| `refactor` | 리팩터링 (기능 변경 없음) |
| `docs`     | 문서 변경                 |
| `style`    | 코드 포맷팅, 세미콜론 등  |
| `test`     | 테스트 추가/수정          |
| `chore`    | 빌드, 설정 등 기타 변경   |
| `ci`       | CI/CD 설정 변경           |
| `perf`     | 성능 개선                 |

### Scope

선택사항. 해당 앱/패키지명을 사용한다: `web`, `backend-graphene`, `backend-strawberry` 등.
