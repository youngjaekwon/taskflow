git log 기반으로 Conventional Commits 형식의 CHANGELOG를 생성하라.

## 입력

$ARGUMENTS

## 절차

1. $ARGUMENTS가 있으면 해당 범위(예: `v1.0.0..HEAD`, `--since="2025-01-01"`)를 사용한다
2. $ARGUMENTS가 없으면 가장 최근 태그부터 HEAD까지를 범위로 한다. 태그가 없으면 전체 히스토리를 사용한다
3. `git log --oneline --no-merges <범위>`로 커밋 목록을 가져온다
4. Conventional Commits의 type별로 분류한다:
   - Features (`feat`)
   - Bug Fixes (`fix`)
   - Refactoring (`refactor`)
   - Documentation (`docs`)
   - Tests (`test`)
   - Chores (`chore`, `ci`, `perf`, `style`)
5. 결과를 마크다운으로 출력한다

## 출력 형식

```
## [Unreleased] - YYYY-MM-DD

### Features
- <subject> (<hash>)

### Bug Fixes
- <subject> (<hash>)

### Refactoring
- <subject> (<hash>)
...
```

## 행동 규칙

- 파일을 직접 수정하지 않는다. 결과만 출력한다
- scope가 있으면 `**scope**: subject` 형태로 표시한다
