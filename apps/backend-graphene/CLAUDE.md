# backend-graphene CLAUDE.md

이 파일은 backend-graphene 앱 고유의 코딩 컨벤션을 정의한다. 모노레포 전체 정보는 루트 CLAUDE.md를 참조한다.

## 1. 개발 방법론 (TDD)

- 모든 기능은 TDD 사이클을 따른다: RED → GREEN → REFACTOR
- 테스트를 먼저 작성한 후 구현 코드를 작성한다
- 테스트 없는 코드는 커밋하지 않는다

## 2. 프로젝트 구조

- `config/`: Django 프로젝트 설정 (settings, urls, wsgi, asgi, 루트 schema)
- 각 Django 앱 내 GraphQL 파일 분리: `types.py`, `queries.py`, `mutations.py`, `schema.py`, `filters.py`, `loaders.py`
- 앱별 `tests/` 디렉터리: `conftest.py`, `factories.py`, `test_models.py`, `test_queries.py`, `test_mutations.py`
- 루트 schema는 앱별 Query/Mutation을 다중 상속으로 합성

## 3. 설정 구조

- `config/settings/` 아래 환경별 분리: `base.py`, `local.py`, `test.py`
- `ATOMIC_MUTATIONS = True` 설정

## 4. 네이밍 컨벤션

| 대상 | 규칙 |
|------|------|
| DjangoObjectType | `{Model}Type` |
| Input 타입 | `{동사}{명사}Input` |
| Mutation 클래스 | `{동사}{명사}` |
| Query 필드명 | 명사만 사용 (get/list 접두어 금지) |
| Resolver | `resolve_{필드명}` |
| Enum 값 | `SCREAMING_SNAKE_CASE` |
| Filter | `{Model}Filter` |
| DataLoader (단일) | `{Model}ByIdLoader` |
| DataLoader (역방향/M2M) | `{Models}By{FK}Loader` |

- Python snake_case → GraphQL camelCase 자동 변환에 의존

## 5. GraphQL 스키마 및 검증

- DjangoObjectType의 `fields`는 명시적 화이트리스트 (`__all__` 금지)
- DRF Serializer는 REST API의 유효성 검증에만 사용
- GraphQL mutation의 유효성 검증은 Django 모델 검증(`clean_fields`)을 사용
- GraphQL과 DRF 계층은 결합하지 않는다

## 6. N+1 쿼리 최적화 (Promise DataLoader)

### 6.1 기본 원칙

- graphene-django에는 N+1 자동 해결 내장 기능이 없으므로 DataLoader로 해결한다
- Promise 기반 DataLoader를 사용한다: `promise` + `graphql-core-promise` 패키지 조합
- 각 Django 앱에 `loaders.py` 파일을 두고 `promise.dataloader.DataLoader`를 상속한 클래스를 정의한다
- DataLoader 네이밍: 단일 조회는 `{Model}ByIdLoader`, 역방향/M2M은 `{Models}By{FK}Loader`, 집계는 `{집계대상}By{FK}Loader`
- `batch_load_fn`의 반환값은 입력 keys와 동일한 순서·길이를 보장해야 한다
- mutation 이후 관련 loader의 `clear(key)` 또는 `clear_all()`로 캐시를 무효화한다

### 6.2 인프라 구성

- `config/views.py`: `CustomGraphQLView(GraphQLView)`에 `execution_context_class=PromiseExecutionContext` 설정
- `config/context.py`: `GQLContext` 클래스가 요청별 DataLoader 인스턴스를 `@cached_property`로 관리
  - `__getattr__`로 Django request 속성에 투명하게 접근
  - `@property`로 `user` 속성 노출
- `config/urls.py`: `CustomGraphQLView.as_view(graphiql=True)`로 등록

### 6.3 batch_load_fn 구현 패턴

| 패턴 | 용도 | ORM 기법 | 기본값 |
|------|------|----------|--------|
| By ID | 단일 PK 조회 | `Model.objects.in_bulk(keys)` | `None` |
| 역방향 FK | 일대다 관계 | `filter(fk__in=keys)` + `defaultdict(list)` 그룹핑 | `[]` |
| M2M | 다대다 관계 | `Model.field.through.objects.filter(...).select_related()` + `defaultdict(list)` | `[]` |
| 집계 (Count) | 배치 카운트 | `filter().values_list().annotate(Count).values_list()` → `dict()` | `0` |

### 6.4 DjangoObjectType에서의 DataLoader 사용 규칙

- **관계 필드를 Meta.fields에서 제거**하고 클래스 본문에 `graphene.Field()`로 명시 선언한다
- 모든 관계 필드에 `resolve_{필드명}` 메서드를 정의하고 `info.context.{loader_name}.load(key)`를 반환한다
- nullable FK는 `if self.xxx_id is None: return None` 가드를 추가한다
- 순환 참조 타입은 문자열(`"app.types.TypeName"`) 또는 `lambda`로 지연 참조한다

### 6.5 Query에서의 DataLoader 공존 규칙

- DataLoader가 처리하는 관계에 대해 `select_related()` / `prefetch_related()`를 사용하지 않는다 (중복 쿼리 방지)
- 루트 쿼리의 `filter()`, `order_by()` 등 QuerySet 조작은 그대로 유지한다

## 7. 테스트 컨벤션

- pytest + pytest-django 사용
- DB 접근 테스트에 `@pytest.mark.django_db` 필수
- conftest.py 계층 구조: 프로젝트 루트(공유) + 앱별(전용)
- factory_boy + pytest-factoryboy `register()` 패턴으로 테스트 데이터 관리
- 팩토리는 `tests/factories.py`에 정의
- GraphQL 쿼리 문자열은 테스트 클래스의 클래스 상수로 선언
- 테스트 3계층: 단위(모델) → 스키마(graphene.test.Client) → 통합(HTTP graphql_query)
