import { USER_BASIC_FRAGMENT } from './user';

export const TASK_CARD_FRAGMENT = `
  fragment TaskCard on TaskType {
    id
    title
    status
    priority
    position
    assignee {
      ...UserBasic
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
    commentCount
  }
  ${USER_BASIC_FRAGMENT}
`;

export const TASK_DETAIL_FRAGMENT = `
  fragment TaskDetail on TaskType {
    id
    title
    description
    status
    priority
    position
    taskGroup {
      id
      name
    }
    assignee {
      ...UserBasic
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
    commentCount
    createdAt
    updatedAt
  }
  ${USER_BASIC_FRAGMENT}
`;
