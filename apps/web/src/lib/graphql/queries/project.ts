import { USER_BASIC_FRAGMENT } from '../fragments/user';

export const PROJECTS_QUERY = `
  query Projects($organizationId: ID!) {
    projects(organizationId: $organizationId) {
      id
      name
      slug
      description
      members {
        id
        user {
          ...UserBasic
        }
      }
    }
  }
  ${USER_BASIC_FRAGMENT}
`;

export const PROJECT_QUERY = `
  query Project($id: ID!) {
    project(id: $id) {
      id
      name
      slug
      description
      organization {
        id
        name
      }
      createdBy {
        id
        email
      }
      createdAt
      updatedAt
      members {
        id
        joinedAt
        user {
          ...UserBasic
        }
        addedBy {
          id
          email
        }
      }
    }
  }
  ${USER_BASIC_FRAGMENT}
`;
