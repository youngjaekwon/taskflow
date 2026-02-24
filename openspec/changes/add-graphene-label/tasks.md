## 0. 앱 스캐폴딩

- [ ] 0.1 `labels` Django 앱 생성 (`python manage.py startapp labels`)
- [ ] 0.2 `config/settings/base.py`의 `INSTALLED_APPS`에 `labels` 추가
- [ ] 0.3 `labels/tests/` 디렉토리 구조 생성 (`__init__.py`, `conftest.py`, `factories.py`)

## 1. Label 모델 (RED -> GREEN)

- [ ] 1.1 `LabelFactory` 작성 (`labels/tests/factories.py`)
- [ ] 1.2 모델 테스트 작성 (`labels/tests/test_models.py`) -- 필드 기본값, unique_together 제약조건, color 검증
- [ ] 1.3 `Label` 모델 구현 (`labels/models.py`) -- name, color(hex), organization FK, created_by
- [ ] 1.4 마이그레이션 생성 및 적용 (`python manage.py makemigrations labels`)
- [ ] 1.5 테스트 통과 확인

## 2. Task-Label M2M 관계

- [ ] 2.1 Task 모델에 `labels` ManyToManyField 추가 (`tasks/models.py`)
- [ ] 2.2 마이그레이션 생성 및 적용
- [ ] 2.3 기존 Task 테스트 통과 확인

## 3. GraphQL 타입 및 데코레이터

- [ ] 3.1 `LabelType` 정의 (`labels/types.py`)
- [ ] 3.2 Input 타입 정의 -- `CreateLabelInput`, `UpdateLabelInput`, `AddLabelsToTaskInput`, `RemoveLabelsFromTaskInput`
- [ ] 3.3 `labels/decorators.py` -- label 접근 권한 데코레이터 (`label_access_required`)
- [ ] 3.4 `TaskType`에 `labels` 필드 추가 (`tasks/types.py`)
- [ ] 3.5 `TaskFilterInput`에 `label_ids` 필드 추가 (`tasks/types.py`)

## 4. createLabel 뮤테이션 (RED -> GREEN)

- [ ] 4.1 테스트 작성 (`labels/tests/test_mutations.py: TestCreateLabel`) -- 성공, 색상 미지정, 중복 이름, 잘못된 색상, 빈 이름, MEMBER 권한 거부, 비소속 거부, 미인증
- [ ] 4.2 `CreateLabel` 뮤테이션 구현 (`labels/mutations.py`)
- [ ] 4.3 테스트 통과 확인

## 5. updateLabel 뮤테이션 (RED -> GREEN)

- [ ] 5.1 테스트 작성 (`labels/tests/test_mutations.py: TestUpdateLabel`) -- 성공(부분 업데이트), 중복 이름, 잘못된 색상, MEMBER 권한 거부, 존재하지 않는 Label, 미인증
- [ ] 5.2 `UpdateLabel` 뮤테이션 구현 (`labels/mutations.py`)
- [ ] 5.3 테스트 통과 확인

## 6. deleteLabel 뮤테이션 (RED -> GREEN)

- [ ] 6.1 테스트 작성 (`labels/tests/test_mutations.py: TestDeleteLabel`) -- 성공(M2M 관계 자동 제거), MEMBER 권한 거부, 존재하지 않는 Label, 미인증
- [ ] 6.2 `DeleteLabel` 뮤테이션 구현 (`labels/mutations.py`)
- [ ] 6.3 테스트 통과 확인

## 7. labels 쿼리 (RED -> GREEN)

- [ ] 7.1 테스트 작성 (`labels/tests/test_queries.py: TestLabelList`) -- Org 멤버 조회, 비소속 거부, 미인증
- [ ] 7.2 `LabelQuery` 구현 (`labels/queries.py`) -- `labels(organizationId)` resolver
- [ ] 7.3 테스트 통과 확인

## 8. addLabelsToTask 뮤테이션 (RED -> GREEN)

- [ ] 8.1 테스트 작성 (`labels/tests/test_mutations.py: TestAddLabelsToTask`) -- 성공, 다른 Org Label 거부, 이미 할당된 Label 중복 무시, 권한 없음, 미인증
- [ ] 8.2 `AddLabelsToTask` 뮤테이션 구현 (`labels/mutations.py`)
- [ ] 8.3 테스트 통과 확인

## 9. removeLabelsFromTask 뮤테이션 (RED -> GREEN)

- [ ] 9.1 테스트 작성 (`labels/tests/test_mutations.py: TestRemoveLabelsFromTask`) -- 성공, 미할당 Label 무시, 권한 없음, 미인증
- [ ] 9.2 `RemoveLabelsFromTask` 뮤테이션 구현 (`labels/mutations.py`)
- [ ] 9.3 테스트 통과 확인

## 10. Task 필터링 확장 (RED -> GREEN)

- [ ] 10.1 테스트 작성 (`tasks/tests/test_queries.py: TestTaskLabelFilter`) -- label_ids 필터링, OR 조건, 중복 없음
- [ ] 10.2 `TaskQuery`의 `resolve_tasks`에 label_ids 필터 로직 추가 (`tasks/queries.py`)
- [ ] 10.3 테스트 통과 확인

## 11. 스키마 통합 및 최종 검증

- [ ] 11.1 `labels/schema.py` 작성 -- LabelQuery, LabelMutation 조합
- [ ] 11.2 `config/schema.py`에 LabelQuery, LabelMutation 통합
- [ ] 11.3 전체 테스트 실행 (`pytest`) -- 기존 테스트 포함 모두 통과 확인
- [ ] 11.4 린트 실행 (`ruff check`, `ruff format`)
