import graphene
from graphene_django import DjangoObjectType

from organizations.models import Organization, OrganizationMembership


class OrganizationType(DjangoObjectType):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created_at",
            "updated_at",
        ]

    created_by = graphene.Field("users.types.UserType")
    members = graphene.List(lambda: OrganizationMemberType)

    def resolve_created_by(self, info):
        if self.created_by_id is None:
            return None
        return info.context.user_by_id_loader.load(self.created_by_id)

    def resolve_members(self, info):
        return info.context.memberships_by_organization_loader.load(self.id)


class OrganizationMemberType(DjangoObjectType):
    class Meta:
        model = OrganizationMembership
        fields = ["id", "role", "joined_at"]

    user = graphene.Field("users.types.UserType")

    def resolve_user(self, info):
        return info.context.user_by_id_loader.load(self.user_id)


# ── Input Types ──


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
