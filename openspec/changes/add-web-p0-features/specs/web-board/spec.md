## ADDED Requirements

### Requirement: Board Selection

The web app SHALL display available boards for a project, allowing the user to select which board to view.
The web app SHALL load the board list via the GraphQL `boards(projectId)` query.
The web app SHALL navigate to the kanban board view when a board is selected.

#### Scenario: View boards for a project

- **WHEN** a user navigates to a project detail page
- **THEN** the available boards are listed or shown as tabs
- **AND** the user can click a board to navigate to its kanban view

#### Scenario: Single board

- **WHEN** a project has only one board
- **THEN** the user is automatically directed to that board's kanban view

---

### Requirement: Kanban Board View

The web app SHALL provide a kanban board page at `/(app)/orgs/[orgId]/projects/[projectId]/boards/[boardId]` that displays TaskGroups as columns.
The web app SHALL load the board data (including TaskGroups and their Tasks) via the GraphQL `board(id)` query in the server load function.
The web app SHALL render each TaskGroup as a column with its tasks listed vertically, ordered by position.
The web app SHALL display task cards with title, status badge, priority indicator, assignee avatar, and due date.

#### Scenario: View kanban board

- **WHEN** a user navigates to a board page
- **THEN** TaskGroups are displayed as columns from left to right (ordered by position)
- **AND** each column contains task cards ordered by position

#### Scenario: Empty board

- **WHEN** a board has no TaskGroups
- **THEN** an empty state is displayed with an option to create a TaskGroup (for admins)

---

### Requirement: Board Management

The web app SHALL allow ADMIN or higher users to create a new board via a Form Action calling the `createBoard` mutation.
The web app SHALL allow ADMIN or higher users to edit a board's name and description via a Form Action calling the `updateBoard` mutation.
The web app SHALL allow ADMIN or higher users to delete a board via a Form Action calling the `deleteBoard` mutation, with a confirmation dialog.

#### Scenario: Create board

- **WHEN** an ADMIN clicks "create board" and submits a name
- **THEN** the new board is created
- **AND** the user is navigated to the new board's kanban view

#### Scenario: Edit board

- **WHEN** an ADMIN edits the board name or description and submits
- **THEN** the board is updated

#### Scenario: Delete board

- **WHEN** an ADMIN clicks delete on a board and confirms
- **THEN** the board is deleted
- **AND** the user is redirected to the project detail page

---

### Requirement: TaskGroup Management

The web app SHALL allow ADMIN or higher users to create a new TaskGroup within a board via a Form Action calling the `createTaskGroup` mutation.
The web app SHALL allow ADMIN or higher users to edit a TaskGroup's name via a Form Action calling the `updateTaskGroup` mutation.
The web app SHALL allow ADMIN or higher users to delete an empty TaskGroup via a Form Action calling the `deleteTaskGroup` mutation.
The web app SHALL prevent deletion of a TaskGroup that contains tasks and display an appropriate error message.

#### Scenario: Create TaskGroup

- **WHEN** an ADMIN clicks "add column" on the kanban board and provides a name
- **THEN** a new TaskGroup column appears at the end of the board

#### Scenario: Edit TaskGroup name

- **WHEN** an ADMIN edits a TaskGroup column header name
- **THEN** the TaskGroup name is updated

#### Scenario: Delete empty TaskGroup

- **WHEN** an ADMIN deletes a TaskGroup that has no tasks
- **THEN** the column is removed from the board

#### Scenario: Delete TaskGroup with tasks

- **WHEN** an ADMIN attempts to delete a TaskGroup that contains tasks
- **THEN** an error message is displayed indicating the TaskGroup must be empty first

---

### Requirement: TaskGroup Reordering

The web app SHALL allow ADMIN or higher users to reorder TaskGroup columns via drag-and-drop.
The web app SHALL submit the new order to the `reorderTaskGroups` mutation via a client-side API call or Form Action.
The web app SHALL provide visual feedback during the drag operation.

#### Scenario: Reorder TaskGroup columns

- **WHEN** an ADMIN drags a TaskGroup column to a new position
- **THEN** the columns are visually reordered
- **AND** the `reorderTaskGroups` mutation is called with the complete list of TaskGroup IDs in new order
- **AND** the updated positions are persisted
