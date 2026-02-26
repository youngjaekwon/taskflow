import { USER_BASIC_FRAGMENT } from '../fragments/user';

export const ME_QUERY = `
  query Me {
    me {
      id
      email
      username
      firstName
      lastName
      emailVerified
      profileImage
      dateJoined
    }
  }
`;

export const MY_ORGANIZATIONS_QUERY = `
  query MyOrganizations {
    myOrganizations {
      id
      name
      slug
      description
      createdAt
      members {
        id
        role
        user {
          ...UserBasic
        }
      }
    }
  }
  ${USER_BASIC_FRAGMENT}
`;
