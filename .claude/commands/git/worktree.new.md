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

브랜치명을 직접 받는다: `<type>/<scope>/<subject>` 또는 `<type>/<subject>`

## 절차

1. `$ARGUMENTS`가 비어있으면 아래 **사용법 안내**를 출력하고 종료한다
2. `$ARGUMENTS`를 파싱하여 type, scope(선택), subject를 추출한다
   - 정규식: `^(feat|fix|refactor|docs|style|test|chore|ci|perf)/(?:([^/]+)/)?([^/]+)$`
   - 3세그먼트(`type/scope/subject`)와 2세그먼트(`type/subject`) 모두 허용한다
   - 파싱 실패 시 올바른 형식을 안내하고 종료한다
3. 워크트리 경로를 조합한다:

   | 항목          | scope 있음                          | scope 없음                  |
   | ------------- | ----------------------------------- | --------------------------- |
   | 브랜치명      | 입력 그대로 사용                    | 입력 그대로 사용            |
   | 워크트리 경로 | `../<type>-<scope>-<subject>` | `../<type>-<subject>` |

4. 동일 브랜치가 이미 존재하는지 `git branch --list <브랜치명>`으로 확인한다
   - 존재하면 "이미 존재하는 브랜치입니다: `<브랜치명>`"을 알리고 종료한다
5. 워크트리 경로가 이미 존재하는지 확인한다
   - 존재하면 "이미 존재하는 경로입니다: `<경로>`"를 알리고 종료한다
6. `git worktree add <워크트리 경로> -b <브랜치명>`을 실행한다
7. `.worktreeinclude` 파일 처리 (공유 파일 복사)
   - 현재 레포 루트에 `.worktreeinclude` 파일이 있는지 확인한다
   - 없으면 이 단계를 건너뛴다
   - 있으면 파일을 읽어 패턴 목록을 파싱한다:
     - 빈 줄과 `#`으로 시작하는 주석은 무시한다
     - 각 줄을 하나의 glob 패턴으로 취급한다
   - 각 패턴에 대해 현재 레포 루트에서 매칭되는 파일/디렉터리를 찾는다
   - 매칭된 항목을 워크트리 경로의 동일 상대 위치로 복사한다:
     - 파일: `cp` 명령으로 복사한다. 필요시 상위 디렉터리를 먼저 생성한다
     - 디렉터리 (`/`로 끝나는 패턴): `cp -r` 명령으로 복사한다
   - 매칭되는 파일이 없는 패턴은 조용히 건너뛴다
8. 생성 결과를 아래 형식으로 출력한다:

```
워크트리가 생성되었습니다.

- 브랜치: `<브랜치명>`
- 경로: `<워크트리 경로>`

해당 디렉터리로 이동하려면:
cd <워크트리 경로>
```

`.worktreeinclude`에서 복사한 파일이 있으면 위 메시지 아래에 추가로 출력한다:

```
복사된 공유 파일:
- <복사된 파일/디렉터리 경로 1>
- <복사된 파일/디렉터리 경로 2>
- ...
```

복사된 파일이 없거나 `.worktreeinclude`가 없으면 이 부분은 출력하지 않는다.

## 에러 처리

- `$ARGUMENTS`가 비어있거나 공백만 있으면 사용법을 안내한다
- type이 허용 목록에 없으면 올바른 type 목록을 안내한다
- 파싱 실패 시 올바른 형식 예시를 보여준다
- git worktree add 명령 실패 시 에러 메시지를 그대로 전달한다
- `.worktreeinclude` 파일 파싱 실패 시 경고를 출력하고 워크트리 생성은 계속 진행한다
- 개별 파일 복사 실패 시 해당 파일에 대한 경고를 출력하고 나머지 파일 복사를 계속한다

## 사용법 안내

```
사용법: /git:worktree.new <type>/<scope>/<subject> 또는 <type>/<subject>

예시:
  /git:worktree.new feat/web/add-task-list-component
  /git:worktree.new fix/backend-graphene/handle-empty-query
  /git:worktree.new chore/update-dependencies

Type: feat, fix, refactor, docs, style, test, chore, ci, perf
Scope: 선택사항 (web, backend-graphene, backend-strawberry 등)
```

## 참조 컨벤션

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

### 브랜치명 형식

- scope 있음: `<type>/<scope>/<subject>` (예: `feat/backend-graphene/project-service`)
- scope 없음: `<type>/<subject>` (예: `chore/update-dependencies`)
