import graphene
from graphql import GraphQLError

from organizations.decorators import check_role, get_membership
from organizations.models import Role
from projects.decorators import project_access_required
from projects.models import Project
from projects.types import ProjectType
from users.decorators import login_required


class ProjectQuery(graphene.ObjectType):
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))
    projects = graphene.List(
        graphene.NonNull(ProjectType),
        organization_id=graphene.ID(required=True),
    )

    @project_access_required
    def resolve_project(root, info, id):
        return info.context.project

    @login_required
    def resolve_projects(root, info, organization_id):
        user = info.context.user
        org_membership = get_membership(user, organization_id)
        if not org_membership:
            raise GraphQLError("이 Organization의 멤버가 아닙니다.")

        if check_role(org_membership, Role.ADMIN):
            return Project.objects.filter(organization_id=organization_id)

        return Project.objects.filter(
            organization_id=organization_id,
            memberships__user=user,
        )
