# graphene-auth Specification

## Purpose
TBD - created by archiving change add-graphene-auth. Update Purpose after archive.
## Requirements
### Requirement: User Registration

The system SHALL validate email format and enforce password strength rules during registration.
The system SHALL create a new user with `is_active=True` and `email_verified=False` upon successful registration.
The system SHALL send a verification email upon successful registration.

#### Scenario: Registration success

- **GIVEN** 유효한 이메일과 강한 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/register/` 요청을 보내면
- **THEN** 새 사용자가 생성되고 (`is_active=True`, `email_verified=False`)
- **AND** 이메일 인증 메일이 발송된다
- **AND** 성공 응답이 반환된다

#### Scenario: Registration with duplicate email

- **GIVEN** 이미 등록된 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/register/` 요청을 보내면
- **THEN** 중복 이메일 에러가 반환된다

#### Scenario: Registration with weak password

- **GIVEN** Django 비밀번호 검증기에 통과하지 못하는 약한 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/register/` 요청을 보내면
- **THEN** 비밀번호 강도 부족 에러가 반환된다

#### Scenario: Registration with invalid email format

- **GIVEN** 잘못된 형식의 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/register/` 요청을 보내면
- **THEN** 이메일 형식 에러가 반환된다

---

### Requirement: User Login

The system SHALL issue a JWT access token and a refresh token upon successful authentication with email and password.
The system SHALL reject login attempts from users whose email is not verified.

#### Scenario: Login success

- **GIVEN** 등록되고 이메일 인증이 완료된 사용자의 올바른 자격 증명이 제공된 경우
- **WHEN** `POST /api/v1/auth/login/` 요청을 보내면
- **THEN** JWT 액세스 토큰과 리프레시 토큰이 반환된다
- **AND** 사용자 정보가 함께 반환된다

#### Scenario: Login with wrong password

- **GIVEN** 잘못된 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/login/` 요청을 보내면
- **THEN** 인증 실패 에러가 반환된다

#### Scenario: Login with non-existent email

- **GIVEN** 등록되지 않은 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/login/` 요청을 보내면
- **THEN** 인증 실패 에러가 반환된다

#### Scenario: Login with unverified email

- **GIVEN** 이메일 인증이 완료되지 않은 사용자의 자격 증명이 제공된 경우
- **WHEN** `POST /api/v1/auth/login/` 요청을 보내면
- **THEN** 이메일 미인증 에러가 반환된다

---

### Requirement: Token Refresh

The system SHALL issue a new JWT access token when a valid, non-expired, non-revoked refresh token is provided.

#### Scenario: Token refresh success

- **GIVEN** 유효한 리프레시 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/token/refresh/` 요청을 보내면
- **THEN** 새로운 JWT 액세스 토큰이 반환된다

#### Scenario: Token refresh with expired refresh token

- **GIVEN** 만료된 리프레시 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/token/refresh/` 요청을 보내면
- **THEN** 토큰 만료 에러가 반환된다

#### Scenario: Token refresh with revoked refresh token

- **GIVEN** 이미 블랙리스트된 리프레시 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/token/refresh/` 요청을 보내면
- **THEN** 토큰 무효 에러가 반환된다

---

### Requirement: User Logout

The system SHALL blacklist the provided refresh token to invalidate the user session.
The system SHALL NOT require access token authentication for logout; only a valid refresh token in the request body is required.

#### Scenario: Logout success

- **GIVEN** 유효한 리프레시 토큰이 request body에 제공된 경우
- **WHEN** `POST /api/v1/auth/logout/` 요청을 보내면
- **THEN** 리프레시 토큰이 블랙리스트에 추가된다
- **AND** 해당 토큰으로 더 이상 액세스 토큰을 갱신할 수 없다

#### Scenario: Logout with already blacklisted token

- **GIVEN** 이미 블랙리스트된 리프레시 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/logout/` 요청을 보내면
- **THEN** 이미 블랙리스트된 토큰 에러가 반환된다

---

### Requirement: Email Verification

The system SHALL send a verification email with a time-limited token during registration.
The system SHALL verify email ownership when a valid token is provided via `POST /api/v1/auth/email/verify/`.
The system SHALL allow resending the verification email for unverified users. Resend is an unauthenticated endpoint that accepts an email address.

#### Scenario: Email verification success

- **GIVEN** 유효한 인증 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/verify/` 요청을 보내면
- **THEN** 사용자의 이메일 인증 상태가 `True`로 변경된다

#### Scenario: Email verification with expired token

- **GIVEN** 만료된 인증 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/verify/` 요청을 보내면
- **THEN** 토큰 만료 에러가 반환된다

#### Scenario: Email verification with invalid token

- **GIVEN** 잘못된 인증 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/verify/` 요청을 보내면
- **THEN** 토큰 무효 에러가 반환된다

#### Scenario: Email verification for already verified user

- **GIVEN** 이미 이메일 인증이 완료된 사용자의 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/verify/` 요청을 보내면
- **THEN** 이미 인증됨 에러가 반환된다

#### Scenario: Resend verification email

- **GIVEN** 이메일 인증이 완료되지 않은 사용자의 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/resend/` 요청을 보내면
- **THEN** 새로운 인증 메일이 발송된다

#### Scenario: Resend verification email for already verified user

- **GIVEN** 이미 이메일 인증이 완료된 사용자의 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/resend/` 요청을 보내면
- **THEN** 이미 인증됨 응답이 반환된다

#### Scenario: Resend verification email for non-existent email

- **GIVEN** 등록되지 않은 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/email/resend/` 요청을 보내면
- **THEN** 보안을 위해 성공 응답이 반환된다 (이메일 존재 여부를 노출하지 않음)

---

### Requirement: Password Change

The system SHALL allow authenticated users to change their password after verifying the current password.
The system SHALL enforce password strength rules on the new password.
The system SHALL invalidate all existing refresh tokens for the user upon successful password change.
The system SHALL issue new tokens after a successful password change.

#### Scenario: Password change success

- **GIVEN** 인증된 사용자가 올바른 기존 비밀번호와 유효한 새 비밀번호를 제공한 경우
- **WHEN** `POST /api/v1/auth/password/change/` 요청을 보내면
- **THEN** 비밀번호가 변경되고 새 토큰이 반환된다
- **AND** 해당 사용자의 기존 리프레시 토큰이 전부 무효화된다

#### Scenario: Password change with wrong current password

- **GIVEN** 잘못된 기존 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/password/change/` 요청을 보내면
- **THEN** 기존 비밀번호 불일치 에러가 반환된다

#### Scenario: Password change with weak new password

- **GIVEN** Django 비밀번호 검증기에 통과하지 못하는 약한 새 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/password/change/` 요청을 보내면
- **THEN** 비밀번호 강도 부족 에러가 반환된다

#### Scenario: Password change without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `POST /api/v1/auth/password/change/` 요청을 보내면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Password Reset

The system SHALL provide an email-based password reset flow using time-limited tokens.
The system SHALL NOT reveal whether an email address is registered when processing reset requests.
The system SHALL invalidate all existing refresh tokens for the user upon successful password reset.

#### Scenario: Password reset email request success

- **GIVEN** 등록된 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/password/reset/` 요청을 보내면
- **THEN** 비밀번호 재설정 이메일이 발송된다

#### Scenario: Password reset email for non-existent user

- **GIVEN** 등록되지 않은 이메일이 제공된 경우
- **WHEN** `POST /api/v1/auth/password/reset/` 요청을 보내면
- **THEN** 보안을 위해 성공 응답을 반환한다 (이메일 존재 여부를 노출하지 않음)

#### Scenario: Password reset success

- **GIVEN** 유효한 재설정 토큰과 새 비밀번호가 제공된 경우
- **WHEN** `POST /api/v1/auth/password/reset/confirm/` 요청을 보내면
- **THEN** 비밀번호가 변경된다

#### Scenario: Password reset invalidates existing tokens

- **GIVEN** 유효한 재설정 토큰과 새 비밀번호가 제공되고, 해당 사용자에게 기존 리프레시 토큰이 존재하는 경우
- **WHEN** `POST /api/v1/auth/password/reset/confirm/` 요청을 보내면
- **THEN** 비밀번호가 변경된다
- **AND** 해당 사용자의 기존 리프레시 토큰이 전부 무효화된다

#### Scenario: Password reset with expired token

- **GIVEN** 만료된 재설정 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/password/reset/confirm/` 요청을 보내면
- **THEN** 토큰 만료 에러가 반환된다

#### Scenario: Password reset with invalid token

- **GIVEN** 잘못된 재설정 토큰이 제공된 경우
- **WHEN** `POST /api/v1/auth/password/reset/confirm/` 요청을 보내면
- **THEN** 토큰 무효 에러가 반환된다

---

### Requirement: Profile Retrieval and Update

The system SHALL allow authenticated users to view their profile information via `me` query.
The system SHALL allow authenticated users to update their profile fields (first_name, last_name) via `updateProfile` mutation.
The system MUST reject unauthenticated requests to profile endpoints.

#### Scenario: Profile retrieval success

- **GIVEN** 인증된 사용자인 경우
- **WHEN** `me` query를 호출하면
- **THEN** 사용자의 프로필 정보(이메일, 이름, 프로필 이미지 URL 등)가 반환된다

#### Scenario: Profile retrieval without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `me` query를 호출하면
- **THEN** 인증 필요 에러가 반환된다

#### Scenario: Profile update success

- **GIVEN** 인증된 사용자가 유효한 프로필 정보를 제공한 경우
- **WHEN** `updateProfile` mutation을 호출하면
- **THEN** 프로필 정보가 업데이트되고 갱신된 정보가 반환된다

#### Scenario: Profile update without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `updateProfile` mutation을 호출하면
- **THEN** 인증 필요 에러가 반환된다

---

### Requirement: Profile Image Upload

The system SHALL allow authenticated users to upload a profile image (JPEG, PNG) via RESTful API.
The system SHALL validate file type and file size before saving the profile image.
The system SHALL allow authenticated users to delete their profile image.
The system MUST reject files exceeding 5MB or with types other than JPEG and PNG.

#### Scenario: Profile image upload success

- **GIVEN** 인증된 사용자가 유효한 이미지 파일(JPEG, PNG)을 업로드하는 경우
- **WHEN** `PUT /api/v1/users/me/profile-image` 요청을 보내면
- **THEN** 프로필 이미지가 저장되고 프로필 이미지 URL이 반환된다

#### Scenario: Profile image upload with invalid file type

- **GIVEN** 허용되지 않은 파일 타입(예: .exe, .txt)이 업로드된 경우
- **WHEN** `PUT /api/v1/users/me/profile-image` 요청을 보내면
- **THEN** 파일 타입 에러가 반환된다

#### Scenario: Profile image upload with oversized file

- **GIVEN** 최대 허용 크기를 초과하는 파일이 업로드된 경우
- **WHEN** `PUT /api/v1/users/me/profile-image` 요청을 보내면
- **THEN** 파일 크기 초과 에러가 반환된다

#### Scenario: Profile image upload without authentication

- **GIVEN** 인증되지 않은 요청인 경우
- **WHEN** `PUT /api/v1/users/me/profile-image` 요청을 보내면
- **THEN** 인증 필요 에러가 반환된다

#### Scenario: Profile image delete success

- **GIVEN** 인증된 사용자가 프로필 이미지를 삭제하려는 경우
- **WHEN** `DELETE /api/v1/users/me/profile-image` 요청을 보내면
- **THEN** 프로필 이미지가 삭제되고 성공 응답이 반환된다

