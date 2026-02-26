export const CREATE_BOARD_MUTATION = `
  mutation CreateBoard($input: CreateBoardInput!) {
    createBoard(input: $input) {
      board {
        id
        name
        slug
      }
    }
  }
`;

export const UPDATE_BOARD_MUTATION = `
  mutation UpdateBoard($input: UpdateBoardInput!) {
    updateBoard(input: $input) {
      board {
        id
        name
        description
      }
    }
  }
`;

export const DELETE_BOARD_MUTATION = `
  mutation DeleteBoard($id: ID!) {
    deleteBoard(id: $id) {
      success
    }
  }
`;

export const CREATE_TASK_GROUP_MUTATION = `
  mutation CreateTaskGroup($input: CreateTaskGroupInput!) {
    createTaskGroup(input: $input) {
      taskGroup {
        id
        name
        position
      }
    }
  }
`;

export const UPDATE_TASK_GROUP_MUTATION = `
  mutation UpdateTaskGroup($input: UpdateTaskGroupInput!) {
    updateTaskGroup(input: $input) {
      taskGroup {
        id
        name
      }
    }
  }
`;

export const DELETE_TASK_GROUP_MUTATION = `
  mutation DeleteTaskGroup($input: DeleteTaskGroupInput!) {
    deleteTaskGroup(input: $input) {
      success
    }
  }
`;

export const REORDER_TASK_GROUPS_MUTATION = `
  mutation ReorderTaskGroups($input: ReorderTaskGroupsInput!) {
    reorderTaskGroups(input: $input) {
      taskGroups {
        id
        position
      }
    }
  }
`;
