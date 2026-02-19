import graphene
from graphql import GraphQLError

from organizations.decorators import get_membership
from organizations.models import Organization
from organizations.types import OrganizationType
from users.decorators import login_required


class OrganizationQuery(graphene.ObjectType):
    my_organizations = graphene.List(graphene.NonNull(OrganizationType))
    organization = graphene.Field(
        OrganizationType, id=graphene.ID(required=True)
    )

    @login_required
    def resolve_my_organizations(root, info):
        return Organization.objects.filter(
            memberships__user=info.context.user
        ).distinct()

    @login_required
    def resolve_organization(root, info, id):
        try:
            org = Organization.objects.get(pk=id)
        except Organization.DoesNotExist:
            raise GraphQLError("Organization을 찾을 수 없습니다.")

        membership = get_membership(info.context.user, id)
        if not membership:
            raise GraphQLError("이 Organization의 멤버가 아닙니다.")

        return org
