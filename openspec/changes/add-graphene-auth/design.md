## Context

backend-graphene 앱은 현재 보일러플레이트 상태(Django 코드 없음)이다. P0 인증 서비스 구현을 위해 Django 프로젝트 초기화부터 시작하여 전체 인증 플로우를 구축해야 한다.

주요 제약 사항:
- Python 3.13, Django 5.x
- CLAUDE.md의 TDD 필수, DRF Serializer 기반 검증 컨벤션
- Graphene-Django의 `DjangoObjectType` 명시적 fields 화이트리스트
- Promise DataLoader 패턴 (N+1 최적화)
- `ATOMIC_MUTATIONS = True` 설정 — 모든 mutation이 트랜잭션으로 래핑됨

## Goals / Non-Goals

- Goals:
  - 9개 P0 인증 기능 완전 구현
  - TDD 기반 개발 (모든 기능에 테스트)
  - CLAUDE.md 컨벤션 완전 준수
  - 향후 Organization/Project/Task 도메인 확장 가능한 기반
- Non-Goals:
  - 소셜 로그인 (OAuth) — 현재 구현하지 않되, REST 기반 인증 구조로 향후 OAuth2 확장이 자연스럽도록 설계
  - 2FA (이중 인증)
  - 프론트엔드 연동
  - 프로덕션 배포 설정

## Decisions

### 1. JWT 라이브러리: `djangorestframework-simplejwt`

- **결정**: `djangorestframework-simplejwt`를 사용한다. `django-graphql-jwt`는 사용하지 않는다.
- **근거**:
  - 인증 엔드포인트를 REST API로 구현하므로 DRF 네이티브 JWT 라이브러리가 적합
  - OAuth2 표준 `Bearer` 토큰 형식을 기본 지원하여 향후 소셜 로그인 확장에 유리
  - 활발한 유지보수 및 Python 3.13 호환성 확인
  - Token blacklist 기능 내장으로 로그아웃 구현 간소화
  - `JWTAuthentication`을 GraphQL view에서도 공유하여 인증 로직 통일
- **대안**: `django-graphql-jwt` — GraphQL 전용이라 REST 엔드포인트와 병행 시 이중 인증 레이어 필요, OAuth2 확장 불리

### 2. 인증 엔드포인트: DRF APIView + Serializer

- **결정**: 인증 관련 기능(회원가입, 로그인, 토큰 관리, 이메일 인증, 비밀번호 관리)을 DRF APIView로 구현하고 검증은 Serializer가 담당한다.
- **근거**:
  - OAuth2는 redirect/callback 기반이므로 인증 플로우가 REST API여야 자연스러운 확장이 가능
  - DRF Serializer 기반 검증은 CLAUDE.md 컨벤션에 부합
  - REST 엔드포인트는 표준 HTTP 상태 코드를 활용할 수 있어 에러 처리가 명확
- **패턴**: Serializer를 검증의 단일 진실 공급원으로 사용하고, APIView에서 비즈니스 로직 실행

### 3. 파일 업로드: DRF RESTful 엔드포인트

- **결정**: 프로필 이미지 업로드를 GraphQL 외부의 DRF RESTful 엔드포인트로 구현
  - `PUT /api/v1/users/me/profile-image` — 업로드/교체 (idempotent)
  - `DELETE /api/v1/users/me/profile-image` — 삭제
- **근거**:
  - GraphQL 공식 문서, Apollo 등 업계 컨센서스: 파일 업로드는 GraphQL 밖에서 처리하는 것이 best practice
  - `graphene-file-upload`는 마지막 릴리스 2021.02로 사실상 방치 상태이며 Python 3.13 호환성 미확인
  - multipart request를 GraphQL 레이어에서 처리 시 보안 리스크 증가
  - CLAUDE.md의 DRF Serializer 기반 검증 컨벤션과 자연스럽게 부합
- **대안**: `graphene-file-upload` — 유지보수 중단, 호환성 리스크로 기각

### 4. 이메일 발송: 개발환경 Console Backend

- **결정**: `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"` (개발환경)
- **근거**: 외부 SMTP 의존성 없이 이메일 플로우 검증 가능
- **확장**: 프로덕션 설정 시 `django-ses`, `sendgrid` 등으로 교체

### 5. 토큰 전달 방식: Authorization 헤더 (Bearer)

- **결정**: `Authorization: Bearer <token>` 헤더 방식 (OAuth2 표준)
- **근거**:
  - OAuth2/RFC 6750 표준 형식으로 향후 소셜 로그인 확장 시 호환
  - `djangorestframework-simplejwt`의 기본 헤더 형식
  - GraphQL 클라이언트(Apollo, urql)에서도 동일한 헤더 방식 사용 가능
- **대안**: `JWT <token>` — 비표준, OAuth2 확장 시 불일치 발생

### 6. 이메일 인증 토큰: Django 내장 token generator 활용

- **결정**: `django.contrib.auth.tokens.PasswordResetTokenGenerator`를 확장하여 이메일 인증/비밀번호 초기화 토큰 생성
- **근거**: Django 내장 기능으로 보안성 검증됨, 별도 의존성 불필요
- **토큰 형식**:
  - `uid`: user pk를 base64 URL-safe 인코딩한 문자열
  - `token`: TokenGenerator가 생성한 시간 제한 문자열
- **전달 방식**: POST body `{"uid": "...", "token": "..."}`
- **이메일 링크**: `{FRONTEND_URL}/auth/verify-email?uid={uid}&token={token}`
  - 프론트엔드가 URL 파라미터를 파싱하여 백엔드 API(`POST /api/v1/auth/email/verify/`)를 호출
  - `FRONTEND_URL`은 settings에서 환경별 설정 (`local.py`, `production.py` 등)

### 7. User 모델 설계: `AbstractUser` 확장

- **결정**: `AbstractUser`를 상속하여 `email` (unique), `profile_image` (ImageField), `email_verified` (BooleanField) 필드 추가
- **근거**: Django 기본 인증 시스템과 완전 호환, `username` + `email` 둘 다 유지
- **인증 필드**: `USERNAME_FIELD = "email"` (이메일로 로그인)
- **`username` 처리 전략**:
  - `blank=True` 설정 — 회원가입 시 사용자가 직접 입력하지 않음
  - 자동 생성: `user_{uuid[:8]}` 형식 (예: `user_a1b2c3d4`)
  - `REQUIRED_FIELDS = ["username"]` — `createsuperuser` CLI 호환성 유지

### 8. REST/GraphQL 경계

- **결정**: 인증 관련 기능은 REST API (`/api/v1/auth/...`), 데이터 조회/수정은 GraphQL (`me` query, `updateProfile` mutation)
- **근거**:
  - 인증은 상태 변경(토큰 발급/폐기, 비밀번호 변경) 중심이므로 REST의 명확한 HTTP 상태 코드가 적합
  - 데이터 조회/수정은 GraphQL의 유연한 필드 선택이 유리
  - OAuth2 확장 시 인증 플로우가 이미 REST이므로 자연스러운 통합 가능
- **GraphQL 인증 연동**: simplejwt의 `JWTAuthentication`을 `GraphQLView`에서도 사용하여 인증 로직 통일

### 9. RESTful URL 구조

- **결정**: 인증 REST API는 `/api/v1/auth/` 네임스페이스 아래에 배치
- **URL 맵핑**:
  ```
  POST /api/v1/auth/register/                 # 회원가입
  POST /api/v1/auth/login/                    # 로그인 (토큰 발급)
  POST /api/v1/auth/logout/                   # 로그아웃 (토큰 무효화)
  POST /api/v1/auth/token/refresh/            # 토큰 리프레시
  POST /api/v1/auth/email/verify/             # 이메일 인증
  POST /api/v1/auth/email/resend/             # 인증 메일 재발송
  POST /api/v1/auth/password/change/          # 비밀번호 변경
  POST /api/v1/auth/password/reset/           # 비밀번호 초기화 요청
  POST /api/v1/auth/password/reset/confirm/   # 비밀번호 초기화 확인
  ```
- **근거**:
  - 리소스 기반 URL 구조로 API 디스커버리 용이
  - `/api/v1/` 버전 프리픽스로 향후 API 버전 관리 가능
  - 기존 프로필 이미지 REST API (`/api/v1/users/me/profile-image`)와 네임스페이스 일관성 유지

### 10. 로그아웃 인증 정책

- **결정**: 로그아웃은 액세스 토큰 인증을 요구하지 않고, 리프레시 토큰 단독 검증으로 처리한다.
- **구현**:
  - `permission_classes = [AllowAny]`
  - Request body에서 `refresh_token`을 수신하여 블랙리스트 처리
- **근거**:
  - 액세스 토큰이 만료된 상태에서도 로그아웃 가능해야 함
  - 리프레시 토큰 자체가 세션의 유효성을 나타내므로 이를 무효화하는 것이 로그아웃의 본질
  - 액세스 토큰 만료 → 리프레시 불가 → 강제 로그아웃 상태가 되지만, 클라이언트는 명시적 로그아웃으로 리프레시 토큰을 정리해야 함

### 11. GraphQL View 인증 연동

- **결정**: `JWTAuthenticationMiddleware` (`users/middleware.py`)를 Django 미들웨어로 구현하여 모든 요청에서 Authorization 헤더를 파싱, `request.user`를 설정한다.
- **REST View 연동**: DRF `authentication_classes`가 자체적으로 인증을 처리하므로 미들웨어와 충돌 없음 (DRF는 미들웨어 설정을 무시하고 자체 인증 사용)
- **GraphQL View 연동**: 미들웨어가 유일한 인증 경로. Resolver에서 커스텀 `@login_required` 데코레이터로 접근 제어
- **커스텀 데코레이터**: `django-graphql-jwt` 미사용이므로 해당 패키지의 `@login_required`를 사용할 수 없음. `info.context.user.is_authenticated`를 검사하는 커스텀 데코레이터를 구현
- **근거**: 단일 미들웨어로 REST/GraphQL 양쪽의 인증 상태를 통일하면서, 각 프레임워크의 인증 메커니즘과 자연스럽게 공존

### 12. 프로필 이미지 저장 전략

- **결정**: 프로필 이미지를 Django `MEDIA_ROOT` 하위에 사용자별 디렉터리로 저장한다.
- **저장 경로**: `MEDIA_ROOT/profile_images/{user_id}/{filename}`
- **제약 조건**:
  - 최대 크기: 5MB
  - 허용 타입: JPEG, PNG
- **교체/삭제 동작**:
  - 이미지 교체 시 기존 파일 물리 삭제 후 새 파일 저장
  - `DELETE` 요청 시 물리 파일 삭제 + DB 필드 null 처리
- **근거**: 사용자별 디렉터리 분리로 파일 충돌 방지, 물리 삭제로 스토리지 낭비 방지

## Risks / Trade-offs

- `djangorestframework-simplejwt`와 GraphQL 인증 연동: simplejwt의 `JWTAuthentication`을 DRF 미들웨어로 사용하고, GraphQL view에서도 동일한 인증 백엔드를 공유한다. `graphene-django`의 `GraphQLView`에 DRF의 `authentication_classes`를 직접 설정하거나, 커스텀 미들웨어로 연동한다.
- 커스텀 구현 시 구현량 증가 → TDD로 품질 보장, 각 기능을 독립적 태스크로 분리
- REST/GraphQL 이중 엔드포인트 관리 → 인증(REST)과 데이터(GraphQL)를 명확히 분리하여 혼선 방지
- Rate Limiting 미구현: P0 단계에서는 별도의 요청 제한을 구현하지 않는다. P1에서 DRF throttling 클래스 또는 리버스 프록시(Nginx 등) 레벨의 rate limiting으로 대응 예정. 특히 로그인, 비밀번호 초기화, 이메일 재발송 엔드포인트는 brute force 공격에 취약할 수 있으므로 P1 우선 대상이다.

## Open Questions

- (없음 — 추가 질문 발생 시 구현 단계에서 업데이트)
