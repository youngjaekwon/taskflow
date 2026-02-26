import { USER_BASIC_FRAGMENT } from '../fragments/user';

export const CREATE_PROJECT_MUTATION = `
  mutation CreateProject($input: CreateProjectInput!) {
    createProject(input: $input) {
      project {
        id
        name
        slug
      }
    }
  }
`;

export const UPDATE_PROJECT_MUTATION = `
  mutation UpdateProject($input: UpdateProjectInput!) {
    updateProject(input: $input) {
      project {
        id
        name
        description
      }
    }
  }
`;

export const DELETE_PROJECT_MUTATION = `
  mutation DeleteProject($id: ID!) {
    deleteProject(id: $id) {
      success
    }
  }
`;

export const ADD_PROJECT_MEMBER_MUTATION = `
  mutation AddProjectMember($input: AddProjectMemberInput!) {
    addProjectMember(input: $input) {
      projectMember {
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

export const REMOVE_PROJECT_MEMBER_MUTATION = `
  mutation RemoveProjectMember($input: RemoveProjectMemberInput!) {
    removeProjectMember(input: $input) {
      success
    }
  }
`;
