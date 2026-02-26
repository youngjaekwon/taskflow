import { USER_BASIC_FRAGMENT } from '../fragments/user';

export const CREATE_ORGANIZATION_MUTATION = `
  mutation CreateOrganization($input: CreateOrganizationInput!) {
    createOrganization(input: $input) {
      organization {
        id
        name
        slug
      }
    }
  }
`;

export const UPDATE_ORGANIZATION_MUTATION = `
  mutation UpdateOrganization($input: UpdateOrganizationInput!) {
    updateOrganization(input: $input) {
      organization {
        id
        name
        description
      }
    }
  }
`;

export const DELETE_ORGANIZATION_MUTATION = `
  mutation DeleteOrganization($id: ID!) {
    deleteOrganization(id: $id) {
      success
    }
  }
`;

export const INVITE_MEMBER_MUTATION = `
  mutation InviteMember($input: InviteMemberInput!) {
    inviteMember(input: $input) {
      membership {
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

export const UPDATE_MEMBER_ROLE_MUTATION = `
  mutation UpdateMemberRole($input: UpdateMemberRoleInput!) {
    updateMemberRole(input: $input) {
      membership {
        id
        role
      }
    }
  }
`;

export const REMOVE_MEMBER_MUTATION = `
  mutation RemoveMember($input: RemoveMemberInput!) {
    removeMember(input: $input) {
      success
    }
  }
`;
