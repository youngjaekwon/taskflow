## ADDED Requirements

### Requirement: Project List Page

The web app SHALL provide a page at `/(app)/orgs/[orgId]/projects` that displays all projects in the organization accessible to the current user.
The web app SHALL load the project list via the GraphQL `projects(organizationId)` query in the server load function.
The web app SHALL display each project's name, description, and member count.
The web app SHALL provide a link to create a new project for ADMIN or higher users.

#### Scenario: View project list (admin)

- **WHEN** an ADMIN or OWNER navigates to the projects page
- **THEN** all projects in the organization are listed

#### Scenario: View project list (member)

- **WHEN** a MEMBER navigates to the projects page
- **THEN** only projects they are assigned to are listed

#### Scenario: No projects

- **WHEN** there are no accessible projects
- **THEN** an empty state is displayed

---

### Requirement: Project Creation

The web app SHALL provide a page at `/(app)/orgs/[orgId]/projects/new` with a form to create a new project.
The web app SHALL only be accessible to ADMIN or higher users.
The web app SHALL submit the project name and description to the `createProject` GraphQL mutation via a Form Action.
The web app SHALL redirect to the new project's detail page upon success.
The web app MUST note that the backend automatically creates a default Board and TaskGroups upon project creation.

#### Scenario: Create project

- **WHEN** an ADMIN or OWNER submits a valid project name and optional description
- **THEN** the project is created (with a default Board and TaskGroups)
- **AND** the user is redirected to the project detail page

#### Scenario: Non-admin access denied

- **WHEN** a MEMBER user attempts to access the project creation page
- **THEN** access is denied (redirect or 403 error)

---

### Requirement: Project Detail and Settings

The web app SHALL provide a page at `/(app)/orgs/[orgId]/projects/[projectId]` that displays the project's information and provides navigation to boards and members.
The web app SHALL load the project data via the GraphQL `project(id)` query in the server load function.
The web app SHALL allow ADMIN or higher users to edit the project name and description via a Form Action calling `updateProject`.
The web app SHALL allow ADMIN or higher users to delete the project via a Form Action calling `deleteProject`, with a confirmation dialog.
The web app SHALL redirect to the project list after deletion.

#### Scenario: View project detail

- **WHEN** a user navigates to a project detail page
- **THEN** the project name, description, and navigation to boards/members are displayed

#### Scenario: Update project (admin)

- **WHEN** an ADMIN or OWNER modifies the project info and submits
- **THEN** the project is updated

#### Scenario: Delete project (admin)

- **WHEN** an ADMIN or OWNER clicks delete and confirms
- **THEN** the project is deleted
- **AND** the user is redirected to the project list

---

### Requirement: Project Member Management

The web app SHALL provide a page at `/(app)/orgs/[orgId]/projects/[projectId]/members` for managing project members.
The web app SHALL load the project member list from the `project(id)` query's `members` field.
The web app SHALL allow ADMIN or higher users to add organization members to the project via a Form Action calling `addProjectMember`.
The web app SHALL allow ADMIN or higher users to remove members from the project via a Form Action calling `removeProjectMember`.
The web app SHALL display a selectable list of organization members who are not yet project members when adding.

#### Scenario: View project members

- **WHEN** a user navigates to the project members page
- **THEN** all project members are listed

#### Scenario: Add project member

- **WHEN** an ADMIN selects an organization member and adds them to the project
- **THEN** the `addProjectMember` mutation is called
- **AND** the new member appears in the list

#### Scenario: Remove project member

- **WHEN** an ADMIN clicks remove on a project member and confirms
- **THEN** the `removeProjectMember` mutation is called
- **AND** the member is removed from the list
