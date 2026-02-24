## ADDED Requirements

### Requirement: Organization List Page

The web app SHALL provide a page at `/(app)/orgs` that displays all organizations the current user belongs to.
The web app SHALL load the organization list via the GraphQL `myOrganizations` query in the server load function.
The web app SHALL display each organization's name, description, member count, and the user's role.
The web app SHALL provide a link to create a new organization.

#### Scenario: View organization list

- **WHEN** an authenticated user navigates to the organizations page
- **THEN** all organizations they belong to are listed with name, description, member count, and their role

#### Scenario: No organizations

- **WHEN** a user has no organization memberships
- **THEN** an empty state is displayed with a prompt to create a new organization

---

### Requirement: Organization Creation

The web app SHALL provide a page at `/(app)/orgs/new` with a form to create a new organization.
The web app SHALL submit the organization name and description to the `createOrganization` GraphQL mutation via a Form Action.
The web app SHALL redirect to the new organization's detail page upon success.
The web app SHALL display validation errors on the form.

#### Scenario: Create organization

- **WHEN** a user submits a valid name and optional description
- **THEN** the organization is created
- **AND** the user is redirected to the organization detail page

#### Scenario: Create organization with invalid data

- **WHEN** a user submits an empty name
- **THEN** a validation error is displayed on the form

---

### Requirement: Organization Detail and Settings

The web app SHALL provide a page at `/(app)/orgs/[orgId]` that displays the organization's detailed information.
The web app SHALL load the organization data via the GraphQL `organization(id)` query in the server load function.
The web app SHALL allow users with ADMIN or higher role to edit the organization name and description via a Form Action calling `updateOrganization`.
The web app SHALL allow users with OWNER role to delete the organization via a Form Action calling `deleteOrganization`, with a confirmation dialog.
The web app SHALL redirect to the organization list after deletion.

#### Scenario: View organization detail

- **WHEN** a user navigates to an organization detail page
- **THEN** the organization name, description, and member information are displayed

#### Scenario: Update organization (admin)

- **WHEN** an ADMIN or OWNER modifies the organization name or description and submits
- **THEN** the organization is updated
- **AND** the updated information is displayed

#### Scenario: Delete organization (owner only)

- **WHEN** an OWNER clicks the delete button and confirms
- **THEN** the organization is deleted
- **AND** the user is redirected to the organization list

#### Scenario: Insufficient permissions for edit

- **WHEN** a MEMBER user views the organization detail page
- **THEN** edit and delete controls are not displayed

---

### Requirement: Member Management Page

The web app SHALL provide a page at `/(app)/orgs/[orgId]/members` that displays all members of the organization.
The web app SHALL load the member list from the `organization(id)` query's `members` field.
The web app SHALL allow ADMIN or higher to invite a new member by email via a Form Action calling `inviteMember`.
The web app SHALL allow ADMIN or higher to change a member's role (ADMIN/MEMBER) via a Form Action calling `updateMemberRole`.
The web app SHALL allow ADMIN or higher to remove a member via a Form Action calling `removeMember`, with confirmation.
The web app SHALL display each member's email, name, role, and join date.

#### Scenario: View member list

- **WHEN** a user navigates to the members page
- **THEN** all organization members are listed with their email, name, role, and join date

#### Scenario: Invite member

- **WHEN** an ADMIN or OWNER submits an email address in the invite form
- **THEN** the `inviteMember` mutation is called
- **AND** the new member appears in the list with MEMBER role

#### Scenario: Invite non-existent user

- **WHEN** an ADMIN invites an email that is not registered
- **THEN** an error message is displayed indicating the user was not found

#### Scenario: Change member role

- **WHEN** an ADMIN or OWNER changes a member's role via the role dropdown
- **THEN** the `updateMemberRole` mutation is called
- **AND** the updated role is reflected in the list

#### Scenario: Remove member

- **WHEN** an ADMIN or OWNER clicks remove on a member and confirms
- **THEN** the `removeMember` mutation is called
- **AND** the member is removed from the list

#### Scenario: Member cannot manage

- **WHEN** a MEMBER user views the members page
- **THEN** invite, role change, and remove controls are not displayed
