import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError

from organizations.decorators import check_role, get_membership
from organizations.models import OrganizationMembership, Role
from projects.decorators import project_admin_required
from projects.models import Project, ProjectMembership
from projects.types import (
    AddProjectMemberInput,
    CreateProjectInput,
    ProjectMemberType,
    ProjectType,
    RemoveProjectMemberInput,
    UpdateProjectInput,
)
from users.decorators import login_required

User = get_user_model()

# ── Helpers ──


def _validate_fields(instance, field_names):
    """변경된 필드에 대해 Django 모델 유효성 검증을 수행한다."""
    exclude = [f.name for f in instance._meta.fields if f.name not in field_names]
    try:
        instance.clean_fields(exclude=exclude)
    except DjangoValidationError as e:
        messages = []
        for field, errors in e.message_dict.items():
            messages.extend(errors)
        raise GraphQLError("; ".join(messages))


# ── Project CRUD ──


class CreateProject(graphene.Mutation):
    class Arguments:
        input = CreateProjectInput(required=True)

    project = graphene.Field(ProjectType)

    @login_required
    def mutate(root, info, input):
        user = info.context.user
        org_membership = get_membership(user, input.organization_id)
        if not org_membership:
            raise GraphQLError("이 Organization의 멤버가 아닙니다.")

        if not check_role(org_membership, Role.ADMIN):
            raise GraphQLError("권한이 부족합니다.")

        data = {
            k: v
            for k, v in dict(input).items()
            if v is not None and k != "organization_id"
        }

        project = Project(
            organization_id=input.organization_id,
            created_by=user,
            **data,
        )
        _validate_fields(project, data)

        project.save()
        ProjectMembership.objects.create(project=project, user=user, added_by=user)
        return CreateProject(project=project)


class UpdateProject(graphene.Mutation):
    class Arguments:
        input = UpdateProjectInput(required=True)

    project = graphene.Field(ProjectType)

    @project_admin_required
    def mutate(root, info, input):
        project = info.context.project

        data = {
            k: v for k, v in dict(input).items() if v is not None and k != "project_id"
        }
        if not data:
            return UpdateProject(project=project)

        if "name" in data:
            project.slug = ""

        for field, value in data.items():
            setattr(project, field, value)

        _validate_fields(project, data)

        project.save()
        return UpdateProject(project=project)


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @project_admin_required
    def mutate(root, info, id):
        project = info.context.project
        project.delete()
        return DeleteProject(success=True)


# ── Member Management ──


class AddProjectMember(graphene.Mutation):
    class Arguments:
        input = AddProjectMemberInput(required=True)

    project_member = graphene.Field(ProjectMemberType)

    @project_admin_required
    def mutate(root, info, input):
        project = info.context.project

        try:
            target_user = User.objects.get(pk=input.user_id)
        except User.DoesNotExist:
            raise GraphQLError("해당 사용자를 찾을 수 없습니다.")

        if not OrganizationMembership.objects.filter(
            organization=project.organization, user=target_user
        ).exists():
            raise GraphQLError("해당 사용자는 이 Organization의 멤버가 아닙니다.")

        if ProjectMembership.objects.filter(project=project, user=target_user).exists():
            raise GraphQLError("이미 이 프로젝트의 멤버입니다.")

        membership = ProjectMembership.objects.create(
            project=project,
            user=target_user,
            added_by=info.context.user,
        )
        return AddProjectMember(project_member=membership)


class RemoveProjectMember(graphene.Mutation):
    class Arguments:
        input = RemoveProjectMemberInput(required=True)

    success = graphene.Boolean()

    @project_admin_required
    def mutate(root, info, input):
        project = info.context.project

        try:
            membership = ProjectMembership.objects.get(
                project=project, user_id=input.user_id
            )
        except ProjectMembership.DoesNotExist:
            raise GraphQLError("이 프로젝트의 멤버가 아닙니다.")

        membership.delete()
        return RemoveProjectMember(success=True)


class ProjectMutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
    add_project_member = AddProjectMember.Field()
    remove_project_member = RemoveProjectMember.Field()
