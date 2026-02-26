import { TASK_CARD_FRAGMENT } from '../fragments/task';

export const BOARDS_QUERY = `
  query Boards($projectId: ID!) {
    boards(projectId: $projectId) {
      id
      name
      slug
      taskGroups {
        id
        name
        position
      }
    }
  }
`;

export const BOARD_QUERY = `
  query Board($id: ID!) {
    board(id: $id) {
      id
      name
      slug
      description
      project {
        id
        name
      }
      createdBy {
        id
        email
      }
      createdAt
      updatedAt
      taskGroups {
        id
        name
        position
        tasks {
          ...TaskCard
        }
      }
    }
  }
  ${TASK_CARD_FRAGMENT}
`;
