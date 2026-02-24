## ADDED Requirements

### Requirement: Route Protection

The web app SHALL protect all routes under the `(app)` route group by checking for valid authentication in `(app)/+layout.server.ts`.
The web app SHALL redirect unauthenticated users to the login page when they attempt to access protected routes.
The web app SHALL redirect already-authenticated users away from auth pages (login, register) to the app dashboard.

#### Scenario: Unauthenticated user accesses protected route

- **WHEN** a user without valid tokens navigates to any `(app)` route
- **THEN** the user is redirected to `/(auth)/login`
- **AND** the original URL is preserved as a redirect parameter

#### Scenario: Authenticated user accesses login page

- **WHEN** a user with valid tokens navigates to `/(auth)/login`
- **THEN** the user is redirected to `/(app)/orgs`

---

### Requirement: Organization Access Verification

The web app SHALL verify that the current user is a member of the organization in the `[orgId]` layout server load.
The web app SHALL load the user's membership role for the organization and make it available to child routes.
The web app SHALL return a 403 error if the user is not a member of the organization.

#### Scenario: Member accesses organization

- **WHEN** a member of an organization navigates to any page under `/(app)/orgs/[orgId]`
- **THEN** the organization data and user's role are loaded
- **AND** the role information is available to all child pages for UI rendering

#### Scenario: Non-member accesses organization

- **WHEN** a user who is not a member of the organization navigates to `/(app)/orgs/[orgId]`
- **THEN** a 403 forbidden error is displayed

---

### Requirement: Project Access Verification

The web app SHALL verify that the current user has access to the project in the `[projectId]` layout server load.
The web app SHALL return a 403 error if the user does not have access.
The web app SHALL load the user's effective permissions for the project (derived from organization role and project membership).

#### Scenario: Authorized user accesses project

- **WHEN** a user with project access navigates to any page under `[projectId]`
- **THEN** the project data is loaded successfully

#### Scenario: Unauthorized user accesses project

- **WHEN** a MEMBER who is not assigned to the project navigates to `[projectId]`
- **THEN** a 403 forbidden error is displayed

#### Scenario: Admin accesses any project

- **WHEN** an organization ADMIN navigates to any project in the organization
- **THEN** the project data is loaded successfully (admins have access to all projects)

---

### Requirement: Role-Based UI Rendering

The web app SHALL conditionally render management controls (edit, delete, invite, role change) based on the user's role.
The web app SHALL use the role data provided by layout loads to determine which UI elements to show.
The web app SHALL hide controls that the user cannot use, rather than showing disabled states.

#### Scenario: Owner sees all controls

- **WHEN** an OWNER views an organization page
- **THEN** all management controls are visible (edit, delete, invite, role change, remove member)

#### Scenario: Admin sees management controls

- **WHEN** an ADMIN views an organization page
- **THEN** management controls are visible except organization delete and ownership transfer

#### Scenario: Member sees read-only view

- **WHEN** a MEMBER views an organization page
- **THEN** only read-only information is displayed without management controls

#### Scenario: Task delete button visibility

- **WHEN** a task's creator or an ADMIN views a task
- **THEN** the delete button is visible
- **WHEN** a MEMBER who is not the creator views a task
- **THEN** the delete button is hidden

---

### Requirement: GraphQL Error Handling

The web app SHALL map GraphQL permission errors to appropriate SvelteKit HTTP errors.
The web app SHALL display user-friendly error messages for authorization failures.
The web app SHALL redirect to the login page when an authentication error is received from the GraphQL API.

#### Scenario: Permission denied error

- **WHEN** a GraphQL request returns a permission denied error
- **THEN** the web app throws a SvelteKit 403 error with a user-friendly message

#### Scenario: Resource not found error

- **WHEN** a GraphQL request returns a "not found" error
- **THEN** the web app throws a SvelteKit 404 error

#### Scenario: Authentication expired during session

- **WHEN** a GraphQL request returns an authentication error after token refresh fails
- **THEN** the user is redirected to the login page
