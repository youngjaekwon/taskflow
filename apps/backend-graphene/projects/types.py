import graphene
from graphene_django import DjangoObjectType

from projects.models import Project, ProjectMembership
from users.types import UserType


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
        ]

    members = graphene.List(lambda: ProjectMemberType)

    def resolve_members(self, info):
        return self.memberships.select_related("user", "added_by").all()


class ProjectMemberType(DjangoObjectType):
    class Meta:
        model = ProjectMembership
        fields = ["id", "joined_at"]

    user = graphene.Field(UserType)
    added_by = graphene.Field(UserType)

    def resolve_user(self, info):
        return self.user

    def resolve_added_by(self, info):
        return self.added_by


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
