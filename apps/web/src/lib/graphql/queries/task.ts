import { TASK_DETAIL_FRAGMENT } from '../fragments/task';

export const TASK_QUERY = `
  query Task($id: ID!) {
    task(id: $id) {
      ...TaskDetail
    }
  }
  ${TASK_DETAIL_FRAGMENT}
`;

export const TASKS_QUERY = `
  query Tasks($projectId: ID!, $filter: TaskFilterInput, $pagination: PaginationInput) {
    tasks(projectId: $projectId, filter: $filter, pagination: $pagination) {
      tasks {
        id
        title
        status
        priority
        assignee {
          id
          email
          username
          firstName
          lastName
          profileImage
        }
        dueDate
        labels {
          id
          name
          color
        }
        createdBy {
          id
          email
        }
      }
      totalCount
      hasNext
      hasPrevious
    }
  }
`;
