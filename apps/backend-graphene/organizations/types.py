import graphene
from graphene_django import DjangoObjectType

from organizations.models import Organization, OrganizationMembership
from users.types import UserType


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        ]

    members = graphene.List(lambda: OrganizationMemberType)

    def resolve_members(self, info):
        return self.memberships.select_related("user").all()


class OrganizationMemberType(DjangoObjectType):
    class Meta:
        model = OrganizationMembership
        fields = ["id", "role", "joined_at"]

    user = graphene.Field(UserType)

    def resolve_user(self, info):
        return self.user


class CreateOrganizationInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String()


class UpdateOrganizationInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()


class InviteMemberInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    email = graphene.String(required=True)


class UpdateMemberRoleInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)
    role = graphene.String(required=True)


class RemoveMemberInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)


class TransferOwnershipInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)
