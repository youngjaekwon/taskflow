export const CREATE_TASK_MUTATION = `
  mutation CreateTask($input: CreateTaskInput!) {
    createTask(input: $input) {
      task {
        id
        title
        position
        status
        priority
      }
    }
  }
`;

export const UPDATE_TASK_MUTATION = `
  mutation UpdateTask($input: UpdateTaskInput!) {
    updateTask(input: $input) {
      task {
        id
        title
        description
        status
        priority
        dueDate
      }
    }
  }
`;

export const DELETE_TASK_MUTATION = `
  mutation DeleteTask($id: ID!) {
    deleteTask(id: $id) {
      success
    }
  }
`;

export const MOVE_TASK_MUTATION = `
  mutation MoveTask($input: MoveTaskInput!) {
    moveTask(input: $input) {
      task {
        id
        taskGroup {
          id
        }
        position
      }
    }
  }
`;

export const REORDER_TASKS_MUTATION = `
  mutation ReorderTasks($input: ReorderTasksInput!) {
    reorderTasks(input: $input) {
      tasks {
        id
        position
      }
    }
  }
`;

export const ASSIGN_TASK_MUTATION = `
  mutation AssignTask($input: AssignTaskInput!) {
    assignTask(input: $input) {
      task {
        id
        assignee {
          id
          email
          username
          firstName
          lastName
          profileImage
        }
      }
    }
  }
`;
