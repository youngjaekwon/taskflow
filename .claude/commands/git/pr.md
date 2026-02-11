---
name: "Git: PR"
description: "커밋, 푸시, PR 생성을 순차적으로 진행"
category: "Git Workflow"
tags: [git, pr]
---

## 입력

$ARGUMENTS

## 절차

### 1. 현재 상태 확인 (병렬 실행)

다음 명령을 **병렬로** 실행하여 현재 상태를 파악한다:

- `git status` — 변경사항 확인
- `git diff --staged` 및 `git diff` — staged/unstaged 변경사항 확인
- `git branch --show-current` — 현재 브랜치 확인
- `git log --oneline -5` — 최근 커밋 히스토리 확인
- `git log main..HEAD --oneline` — PR에 포함될 커밋 목록 확인

### 2. 사전 검증

- 현재 브랜치가 `main`이면 **즉시 중단**하고 "main 브랜치에서는 PR을 생성할 수 없습니다. feature 브랜치에서 실행해주세요."라고 안내한다
- 변경사항이 없고 `main..HEAD` 커밋도 없으면 "커밋할 변경사항과 PR에 포함할 커밋이 없습니다"라고 안내하고 종료한다

### 3. 커밋 생성

변경사항(staged 또는 unstaged)이 있는 경우에만 커밋을 생성한다. 변경사항이 없으면 이 단계를 건너뛴다.

- `/git:commit`의 커밋 컨벤션을 따른다:
  - **제목**: 영어, imperative, Conventional Commits 형식 (`<type>(<scope>): <subject>`)
  - **본문**: 한국어로 변경 이유와 맥락 설명
- 스테이징 전 `.env`, `credentials`, `secret` 등 민감 파일이 변경사항에 포함되어 있는지 확인한다
- 민감 파일이 있으면 사용자에게 경고하고 확인을 받는다
- `git add -A`로 모든 변경사항을 스테이징한다
- 커밋 메시지는 HEREDOC을 사용한다:

  ```bash
  git commit -m "$(cat <<'EOF'
  <type>(<scope>): <subject>

  <body>
  EOF
  )"
  ```

### 4. 푸시

- `-u` 플래그를 사용하여 원격 브랜치를 생성하고 tracking을 설정한다:
  ```bash
  git push -u origin <현재-브랜치>
  ```
- **force push는 절대 사용하지 않는다**

### 5. PR 생성

- `gh pr create --base main`을 사용한다
- **타이틀**: 한국어로 작성, 70자 이내
- **본문**: HEREDOC을 사용하여 다음 구조로 작성한다:

  ```bash
  gh pr create --base main --title "<한국어 타이틀>" --body "$(cat <<'EOF'
  ## Summary
  <변경사항 요약 — 1~3개 bullet point>

  ## Changes
  <main..HEAD의 모든 커밋을 나열>
  - <commit hash> <commit message>
  - ...

  ## Test plan
  - [ ] <테스트 항목>
  - ...
  EOF
  )"
  ```

### 6. 완료 보고

- 생성된 PR URL을 출력한다
- `git status`로 최종 상태를 확인한다

## 행동 규칙

- **force push 금지**: `--force`, `--force-with-lease` 등을 절대 사용하지 않는다
- **새 커밋만 생성**: `--amend`를 사용하지 않는다. 항상 새로운 커밋을 만든다
- **에러 시 즉시 중단**: 어떤 단계에서든 에러가 발생하면 즉시 중단하고 사용자에게 알린다
- **hook 우회 금지**: `--no-verify` 등 hook을 건너뛰는 옵션을 사용하지 않는다
