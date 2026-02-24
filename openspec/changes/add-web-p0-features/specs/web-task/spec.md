## ADDED Requirements

### Requirement: Task Creation

The web app SHALL allow project members to create a new task within a TaskGroup on the kanban board.
The web app SHALL provide a task creation form (modal or inline) with fields: title (required), description, status, priority, assignee, and due date.
The web app SHALL submit the task data to the `createTask` GraphQL mutation via a Form Action.
The web app SHALL display the new task card in the appropriate TaskGroup column upon success.

#### Scenario: Create task with required fields only

- **WHEN** a user fills in a title and submits the task creation form
- **THEN** a new task is created with default status (TODO) and priority (MEDIUM)
- **AND** the task card appears in the target TaskGroup column

#### Scenario: Create task with all fields

- **WHEN** a user fills in title, description, status, priority, assignee, and due date
- **THEN** a new task is created with all specified fields
- **AND** the task card displays the provided information

#### Scenario: Create task with validation error

- **WHEN** a user submits the form without a title
- **THEN** a validation error is displayed

---

### Requirement: Task Detail View

The web app SHALL provide a task detail view (modal or side panel) that displays all task information.
The web app SHALL load task details via the GraphQL `task(id)` query or from already-loaded board data.
The web app SHALL display: title, description, status, priority, assignee (name and avatar), due date, labels, creation date, and creator.

#### Scenario: View task detail

- **WHEN** a user clicks on a task card in the kanban board
- **THEN** the task detail view opens showing all task information

---

### Requirement: Task Update

The web app SHALL allow project members to edit a task's title, description, status, priority, and due date.
The web app SHALL submit updates to the `updateTask` GraphQL mutation via a Form Action.
The web app SHALL reflect the updated information in both the task detail view and the kanban board card.

#### Scenario: Update task fields

- **WHEN** a user modifies task fields in the detail view and submits
- **THEN** the `updateTask` mutation is called with the changed fields
- **AND** the updated information is reflected on the page

---

### Requirement: Task Deletion

The web app SHALL allow task creators and ADMIN or higher users to delete a task.
The web app SHALL display a delete button only for users with deletion permission.
The web app SHALL show a confirmation dialog before deletion.
The web app SHALL submit the deletion to the `deleteTask` GraphQL mutation via a Form Action.

#### Scenario: Delete task (creator)

- **WHEN** the task creator clicks delete and confirms
- **THEN** the task is deleted
- **AND** the task card is removed from the kanban board

#### Scenario: Delete task (admin)

- **WHEN** an ADMIN or OWNER clicks delete on any task and confirms
- **THEN** the task is deleted

#### Scenario: Delete button hidden for non-authorized users

- **WHEN** a MEMBER who is not the task creator views a task
- **THEN** the delete button is not displayed

---

### Requirement: Task Status Change

The web app SHALL allow project members to change a task's status via a status dropdown in the task detail view or task card.
The web app SHALL support the status values: TODO, IN_PROGRESS, IN_REVIEW, DONE.
The web app SHALL submit the status change to the `updateTask` mutation.

#### Scenario: Change task status via dropdown

- **WHEN** a user selects a new status from the status dropdown
- **THEN** the task status is updated
- **AND** the status badge on the task card reflects the new status

---

### Requirement: Task Move Between TaskGroups

The web app SHALL allow project members to move a task to a different TaskGroup via drag-and-drop on the kanban board.
The web app SHALL submit the move to the `moveTask` GraphQL mutation with the target TaskGroup ID and optional position.
The web app SHALL provide visual feedback during the drag operation.
The web app SHALL only allow moves within the same board.

#### Scenario: Drag task to another column

- **WHEN** a user drags a task card from one TaskGroup column to another
- **THEN** the `moveTask` mutation is called
- **AND** the task card appears in the target column at the dropped position

#### Scenario: Move task to specific position

- **WHEN** a user drops a task card between two existing cards in the target column
- **THEN** the task is placed at the correct position in the target TaskGroup

---

### Requirement: Task Reordering

The web app SHALL allow project members to reorder tasks within the same TaskGroup via drag-and-drop.
The web app SHALL submit the new order to the `reorderTasks` mutation with the complete list of task IDs.

#### Scenario: Reorder tasks within a column

- **WHEN** a user drags a task card to a new position within the same TaskGroup column
- **THEN** the task order is updated
- **AND** the `reorderTasks` mutation is called with the new order

---

### Requirement: Task Assignee Management

The web app SHALL allow project members to assign or change a task's assignee via a dropdown in the task detail view.
The web app SHALL display a list of project members as assignee options.
The web app SHALL allow clearing the assignee (unassign).
The web app SHALL submit the assignee change to the `assignTask` mutation.

#### Scenario: Assign task to a member

- **WHEN** a user selects a project member from the assignee dropdown
- **THEN** the `assignTask` mutation is called
- **AND** the assignee avatar is displayed on the task card

#### Scenario: Unassign task

- **WHEN** a user clears the assignee selection
- **THEN** the `assignTask` mutation is called with null assigneeId
- **AND** the assignee indicator is removed from the task card

---

### Requirement: Task List Filtering

The web app SHALL provide filter controls on the kanban board or task list view.
The web app SHALL support filtering by: status (multi-select), priority (multi-select), assignee, due date range (from/to), and keyword search (title and description).
The web app SHALL submit filter criteria as variables to the `tasks` query with `TaskFilterInput`.
The web app SHALL update the displayed tasks to reflect the active filters.
The web app SHALL allow clearing all filters.

#### Scenario: Filter by status

- **WHEN** a user selects one or more status values in the filter
- **THEN** only tasks matching the selected statuses are displayed

#### Scenario: Filter by keyword

- **WHEN** a user enters a search term in the keyword filter
- **THEN** only tasks whose title or description contains the search term are displayed

#### Scenario: Combined filters

- **WHEN** a user applies multiple filters simultaneously
- **THEN** tasks matching all filter criteria are displayed

#### Scenario: Clear filters

- **WHEN** a user clicks the clear filters button
- **THEN** all filters are reset and all tasks are displayed

---

### Requirement: Task List Pagination

The web app SHALL support pagination for the task list using the `PaginationInput` (limit/offset).
The web app SHALL display pagination controls (previous/next) with total count information.
The web app SHALL use the `TaskConnectionType` response (totalCount, hasNext, hasPrevious) to render pagination state.

#### Scenario: Navigate pages

- **WHEN** a user clicks the next page button
- **THEN** the next page of tasks is loaded and displayed
- **AND** the pagination state (current page, total count) is updated

#### Scenario: First page

- **WHEN** the user is on the first page
- **THEN** the previous button is disabled

#### Scenario: Last page

- **WHEN** the user is on the last page
- **THEN** the next button is disabled
