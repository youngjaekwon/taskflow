## 1. Django 프로젝트 초기화

- [x] 1.1 `uv init` 및 `uv add`로 의존성 추가 (Django, graphene-django, djangorestframework, djangorestframework-simplejwt, Pillow, pytest-django, factory-boy 등)
- [x] 1.2 Django 프로젝트 생성 (`config/` 디렉토리, `manage.py`)
- [x] 1.3 settings 분리 구조 설정 (`config/settings/base.py`, `local.py`, `test.py`)
- [x] 1.4 `urls.py` 및 GraphQL 엔드포인트 설정 (`GraphQLView`, `ATOMIC_MUTATIONS = True`)
- [x] 1.5 `package.json` 스크립트 업데이트 (dev, test, lint 실제 명령어로 교체)
- [x] 1.6 Dockerfile 업데이트
- [x] 1.7 Django 서버 기동 및 GraphQL 엔드포인트 동작 확인

## 2. 커스텀 User 모델 및 기본 스키마

- [x] 2.1 `users` Django 앱 생성
- [x] 2.2 `CustomUser` 모델 구현 (`email` unique, `profile_image` ImageField, `email_verified` BooleanField, `username` blank=True)
- [x] 2.3 `AUTH_USER_MODEL` 설정 및 초기 마이그레이션
- [x] 2.4 `UserType` DjangoObjectType 구현 (명시적 fields 화이트리스트)
- [x] 2.5 루트 Query/Mutation 스키마 구성 (`config/schema.py`)
- [x] 2.6 `JWTAuthenticationMiddleware` 스켈레톤 생성 (`users/middleware.py`)
- [x] 2.7 테스트 인프라 구성 (`conftest.py`, `users/factories.py` — UserFactory)
- [x] 2.8 모델 테스트 작성 (`test_models.py`)

## 3. 회원가입 + 인증 메일 발송

- [x] 3.1 `EmailVerificationTokenGenerator` 구현 (`users/tokens.py` — `PasswordResetTokenGenerator` 확장)
- [x] 3.2 `send_verification_email(user)` 유틸리티 함수 구현 (`users/utils.py` — uid base64 인코딩 + 토큰 생성 + 메일 발송)
- [x] 3.3 `RegisterSerializer` 구현 (이메일 형식 검증, 비밀번호 강도 규칙, password confirmation)
- [x] 3.4 `RegisterView` 회원가입 로직 구현 (Serializer.save()로 User 생성 + `user_{uuid[:8]}` username 자동 생성 + `send_verification_email()` 호출)
- [x] 3.5 `RegisterView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/register/`)
- [x] 3.6 URL 등록 (`/api/v1/auth/register/`)
- [x] 3.7 회원가입 테스트 (성공, 중복 이메일, 약한 비밀번호, 잘못된 이메일 형식, username 자동 생성 확인, 인증 메일 발송 확인)

## 4. 이메일 인증 (verify/resend)

- [x] 4.1 `VerifyEmailSerializer` 구현 (uid, token 검증)
- [x] 4.2 `VerifyEmailView` 이메일 인증 로직 구현 (토큰 검증 + email_verified = True)
- [x] 4.3 `VerifyEmailView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/email/verify/`)
- [x] 4.4 `ResendVerificationEmailSerializer` 구현 (email 검증)
- [x] 4.5 `ResendVerificationEmailView` 인증 메일 재발송 로직 구현 (미인증 시 `send_verification_email()` 호출, 미등록 이메일은 보안을 위해 성공 응답)
- [x] 4.6 `ResendVerificationEmailView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/email/resend/`)
- [x] 4.7 URL 등록 (`/api/v1/auth/email/verify/`, `/api/v1/auth/email/resend/`)
- [x] 4.8 이메일 인증 테스트 (인증 성공, 만료된 토큰, 잘못된 토큰, 이미 인증된 사용자, 재발송 성공, 이미 인증된 사용자 재발송, 미등록 이메일 재발송)

## 5. 로그인 + JWT 미들웨어

- [x] 5.1 `djangorestframework-simplejwt` 설정 (SIMPLE_JWT 설정, REST_FRAMEWORK authentication_classes)
- [x] 5.2 `LoginSerializer` 구현 (email, password 검증)
- [x] 5.3 `LoginView` 로그인 로직 구현 (자격 증명 확인 + 이메일 인증 확인 + 토큰 발급)
- [x] 5.4 `LoginView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/login/`)
- [x] 5.5 `JWTAuthenticationMiddleware` 구현 (`users/middleware.py` — Authorization 헤더 파싱 → `request.user` 설정)
- [x] 5.6 커스텀 `@login_required` 데코레이터 구현 (`users/decorators.py` — `info.context.user.is_authenticated` 검사)
- [x] 5.7 로그인 테스트 (성공, 잘못된 비밀번호, 존재하지 않는 사용자, 이메일 미인증)
- [x] 5.8 미들웨어 테스트 (유효한 토큰, 만료된 토큰, 토큰 없음)

## 6. 토큰 리프레시

- [x] 6.1 simplejwt `TokenRefreshView` 설정 (리프레시 관련 SIMPLE_JWT 설정 확인)
- [x] 6.2 `TokenRefreshView` 등록 (`POST /api/v1/auth/token/refresh/`)
- [x] 6.3 토큰 리프레시 테스트 (성공, 만료된 리프레시 토큰, 블랙리스트된 리프레시 토큰)

## 7. 로그아웃

- [x] 7.1 `LogoutView` 로그아웃 로직 구현 (리프레시 토큰 블랙리스트 처리)
- [x] 7.2 `LogoutView` DRF APIView 엔드포인트 등록 — `permission_classes = [AllowAny]`, 리프레시 토큰만 검증 (`POST /api/v1/auth/logout/`)
- [x] 7.3 로그아웃 테스트 (성공, 이미 블랙리스트된 토큰, 액세스 토큰 없이 로그아웃 성공)

## 8. 비밀번호 변경

- [x] 8.1 `invalidate_all_tokens(user)` 유틸리티 함수 구현 (`users/utils.py` — OutstandingToken 일괄 블랙리스트)
- [x] 8.2 `PasswordChangeSerializer` 구현 (기존 비밀번호 확인, 새 비밀번호 강도 검증)
- [x] 8.3 `PasswordChangeView` 비밀번호 변경 로직 구현 (변경 + `invalidate_all_tokens()` 호출 + 새 토큰 발급)
- [x] 8.4 `PasswordChangeView` DRF APIView 엔드포인트 등록 (인증 필수) (`POST /api/v1/auth/password/change/`)
- [x] 8.5 비밀번호 변경 테스트 (성공, 잘못된 기존 비밀번호, 약한 새 비밀번호, 미인증, 기존 토큰 무효화 확인)

## 9. 비밀번호 초기화

- [x] 9.1 `send_password_reset_email(user)` 유틸리티 함수 구현 (`users/utils.py` — uid base64 인코딩 + 토큰 생성 + 메일 발송)
- [x] 9.2 `PasswordResetRequestView` 비밀번호 초기화 요청 로직 구현 (`send_password_reset_email()` 호출, 미등록 이메일에도 성공 응답)
- [x] 9.3 `PasswordResetRequestView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/password/reset/`)
- [x] 9.4 `PasswordResetConfirmView` 비밀번호 초기화 확인 로직 구현 (토큰 검증 + 비밀번호 변경 + `invalidate_all_tokens()` 호출)
- [x] 9.5 `PasswordResetConfirmView` DRF APIView 엔드포인트 등록 (`POST /api/v1/auth/password/reset/confirm/`)
- [x] 9.6 비밀번호 초기화 테스트 (이메일 발송, 미등록 이메일 발송, 성공, 만료된 토큰, 잘못된 토큰, 기존 토큰 무효화 확인)

## 10. 내 프로필 조회/수정

- [x] 10.1 `me` Query 구현 (커스텀 `@login_required`, 로그인한 사용자 정보 반환)
- [x] 10.2 `UpdateProfileSerializer` 구현 (first_name, last_name 수정 가능 필드)
- [x] 10.3 `UpdateProfile` Mutation 구현 (커스텀 `@login_required`)
- [x] 10.4 프로필 조회/수정 테스트 (조회 성공, 수정 성공, 미인증)

## 11. 프로필 이미지 업로드 (RESTful API)

- [x] 11.1 `ProfileImageSerializer` 구현 (파일 타입: JPEG/PNG 검증, 최대 크기: 5MB 검증)
- [x] 11.2 `UserProfileImageView` DRF APIView 구현 (`PUT` 업로드/교체 — 기존 파일 물리 삭제, `DELETE` 삭제 — 물리 삭제 + DB null 처리)
- [x] 11.3 URL 등록 (`/api/v1/users/me/profile-image`)
- [x] 11.4 JWT 인증 연동 (DRF `authentication_classes` — simplejwt `JWTAuthentication`)
- [x] 11.5 프로필 이미지 테스트 (업로드 성공, 잘못된 파일 타입, 5MB 초과 파일 크기, 미인증, 삭제, 교체 시 기존 파일 삭제 확인)

---

**의존 관계**: 1 → 2 → 3 → 4 → 5 → 6,7 (병렬) → 8,9 (병렬) → 10,11 (병렬)

**검증 기준**: 각 단계의 모든 테스트가 통과해야 다음 단계로 진행
