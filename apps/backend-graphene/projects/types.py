import graphene
from graphene_django import DjangoObjectType

from projects.models import Project, ProjectMembership


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created_at",
            "updated_at",
        ]

    organization = graphene.Field("organizations.types.OrganizationType")
    created_by = graphene.Field("users.types.UserType")
    members = graphene.List(lambda: ProjectMemberType)

    def resolve_organization(self, info):
        return info.context.organization_by_id_loader.load(self.organization_id)

    def resolve_created_by(self, info):
        if self.created_by_id is None:
            return None
        return info.context.user_by_id_loader.load(self.created_by_id)

    def resolve_members(self, info):
        return info.context.memberships_by_project_loader.load(self.id)


class ProjectMemberType(DjangoObjectType):
    class Meta:
        model = ProjectMembership
        fields = ["id", "joined_at"]

    user = graphene.Field("users.types.UserType")
    added_by = graphene.Field("users.types.UserType")

    def resolve_user(self, info):
        return info.context.user_by_id_loader.load(self.user_id)

    def resolve_added_by(self, info):
        if self.added_by_id is None:
            return None
        return info.context.user_by_id_loader.load(self.added_by_id)


# ── Input Types ──


class CreateProjectInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()


class UpdateProjectInput(graphene.InputObjectType):
    project_id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()


class AddProjectMemberInput(graphene.InputObjectType):
    project_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)


class RemoveProjectMemberInput(graphene.InputObjectType):
    project_id = graphene.ID(required=True)
    user_id = graphene.ID(required=True)
