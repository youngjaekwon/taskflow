import { USER_BASIC_FRAGMENT } from '../fragments/user';

export const ORGANIZATION_QUERY = `
  query Organization($id: ID!) {
    organization(id: $id) {
      id
      name
      slug
      description
      createdBy {
        id
        email
      }
      createdAt
      updatedAt
      members {
        id
        role
        joinedAt
        user {
          ...UserBasic
        }
      }
    }
  }
  ${USER_BASIC_FRAGMENT}
`;
