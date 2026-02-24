## ADDED Requirements

### Requirement: User Registration Page

The web app SHALL provide a registration page at `/(auth)/register` with email and password input fields.
The web app SHALL validate email format and password strength on the client side before submission.
The web app SHALL submit registration data to the backend REST API (`POST /api/v1/auth/register/`) via a SvelteKit Form Action.
The web app SHALL display server-side validation errors (duplicate email, weak password) inline on the form.
The web app SHALL redirect to a "check your email" confirmation page upon successful registration.

#### Scenario: Successful registration

- **WHEN** a user submits valid email and password on the registration form
- **THEN** the Form Action sends a POST request to the backend register endpoint
- **AND** on success, the user is redirected to a confirmation page indicating a verification email has been sent

#### Scenario: Registration with validation errors

- **WHEN** a user submits invalid data (duplicate email, weak password, invalid email format)
- **THEN** the Form Action returns validation errors
- **AND** the form re-renders with error messages displayed next to the relevant fields

---

### Requirement: User Login Page

The web app SHALL provide a login page at `/(auth)/login` with email and password input fields.
The web app SHALL submit login credentials to the backend REST API (`POST /api/v1/auth/login/`) via a SvelteKit Form Action.
The web app SHALL store the returned JWT access token and refresh token in httpOnly cookies upon successful login.
The web app SHALL redirect authenticated users to the app dashboard after login.
The web app SHALL display appropriate error messages for failed login attempts.

#### Scenario: Successful login

- **WHEN** a user submits valid credentials on the login form
- **THEN** the Form Action sends a POST request to the backend login endpoint
- **AND** on success, JWT tokens are stored in httpOnly cookies
- **AND** the user is redirected to `/(app)/orgs`

#### Scenario: Login with invalid credentials

- **WHEN** a user submits wrong email or password
- **THEN** the form displays an authentication error message

#### Scenario: Login with unverified email

- **WHEN** a user whose email is not verified attempts to login
- **THEN** the form displays an email verification required message with a link to resend

---

### Requirement: Token Management

The web app SHALL automatically read JWT access tokens from httpOnly cookies in `hooks.server.ts` and attach them to `event.locals`.
The web app SHALL automatically refresh expired access tokens using the refresh token cookie by calling the backend token refresh endpoint.
The web app SHALL update the access token cookie when a refresh is successful.
The web app SHALL redirect to the login page and clear cookies when both access and refresh tokens are invalid.

#### Scenario: Automatic token refresh

- **WHEN** a server load function makes a GraphQL request and the access token is expired
- **THEN** the server hook intercepts the response, refreshes the token via the backend endpoint
- **AND** retries the original request with the new token
- **AND** updates the access token cookie in the response

#### Scenario: Token refresh failure

- **WHEN** both the access token and refresh token are expired or invalid
- **THEN** the server hook clears all token cookies
- **AND** redirects the user to the login page

---

### Requirement: User Logout

The web app SHALL provide a logout action accessible from the app navigation.
The web app SHALL submit a logout request to the backend REST API (`POST /api/v1/auth/logout/`) with the refresh token via a SvelteKit Form Action.
The web app SHALL clear all token cookies upon logout.
The web app SHALL redirect to the login page after logout.

#### Scenario: Successful logout

- **WHEN** a user clicks the logout button
- **THEN** the Form Action sends the refresh token to the backend logout endpoint
- **AND** httpOnly token cookies are cleared
- **AND** the user is redirected to the login page

---

### Requirement: Email Verification Page

The web app SHALL provide an email verification page at `/(auth)/verify-email` that accepts a verification token as a query parameter.
The web app SHALL submit the token to the backend REST API (`POST /api/v1/auth/email/verify/`) on page load via server load.
The web app SHALL display the verification result (success, expired token, invalid token, already verified).
The web app SHALL provide a "resend verification email" form that accepts an email address.

#### Scenario: Successful email verification

- **WHEN** a user visits the verification page with a valid token
- **THEN** the server load verifies the token via the backend endpoint
- **AND** a success message is displayed with a link to the login page

#### Scenario: Failed email verification

- **WHEN** a user visits the verification page with an expired or invalid token
- **THEN** an error message is displayed
- **AND** a form to resend the verification email is shown

#### Scenario: Resend verification email

- **WHEN** a user submits their email on the resend form
- **THEN** the Form Action sends a resend request to the backend endpoint
- **AND** a confirmation message is displayed regardless of whether the email exists (security)

---

### Requirement: Password Reset Flow

The web app SHALL provide a forgot password page at `/(auth)/forgot-password` with an email input field.
The web app SHALL submit the email to the backend REST API (`POST /api/v1/auth/password/reset/`) via a Form Action.
The web app SHALL provide a reset password page at `/(auth)/reset-password` that accepts a reset token as a query parameter.
The web app SHALL submit the new password and token to the backend REST API (`POST /api/v1/auth/password/reset/confirm/`) via a Form Action.
The web app SHALL always display a success message after requesting a reset, regardless of email existence (security).

#### Scenario: Request password reset

- **WHEN** a user submits their email on the forgot password page
- **THEN** a confirmation message is displayed saying a reset email has been sent (if the account exists)

#### Scenario: Reset password with valid token

- **WHEN** a user visits the reset password page with a valid token and submits a new password
- **THEN** the password is reset
- **AND** the user is redirected to the login page with a success message

#### Scenario: Reset password with invalid token

- **WHEN** a user visits the reset password page with an expired or invalid token
- **THEN** an error message is displayed with a link to request a new reset email

---

### Requirement: Profile Page

The web app SHALL provide a profile page at `/(app)/profile` that displays the current user's information.
The web app SHALL load profile data via the GraphQL `me` query in the server load function.
The web app SHALL allow editing first name and last name via a Form Action that calls the `updateProfile` GraphQL mutation.
The web app SHALL allow uploading a profile image (JPEG, PNG, max 5MB) via a Form Action that calls the backend REST API (`PUT /api/v1/users/me/profile-image`).
The web app SHALL allow deleting the profile image via a Form Action that calls the backend REST API (`DELETE /api/v1/users/me/profile-image`).
The web app SHALL provide a password change section that accepts current password and new password, submitting to the backend REST API (`POST /api/v1/auth/password/change/`) via a Form Action.

#### Scenario: View profile

- **WHEN** an authenticated user navigates to the profile page
- **THEN** their profile information (email, name, avatar) is displayed

#### Scenario: Update profile

- **WHEN** a user modifies their name and submits the profile form
- **THEN** the `updateProfile` mutation is called
- **AND** the updated profile is displayed

#### Scenario: Upload profile image

- **WHEN** a user selects and uploads a valid image file
- **THEN** the image is uploaded via the REST endpoint
- **AND** the profile image is updated on the page

#### Scenario: Change password

- **WHEN** a user submits the current password and a valid new password
- **THEN** the password is changed via the REST endpoint
- **AND** new tokens are issued and cookies are updated
- **AND** a success message is displayed
