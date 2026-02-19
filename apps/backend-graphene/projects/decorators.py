from functools import wraps

from graphql import GraphQLError

from organizations.decorators import check_role, get_membership
from organizations.models import Role
from projects.models import Project, ProjectMembership


def _get_project(kwargs, args):
    input_arg = kwargs.get("input") or (args[0] if args else None)
    project_id = (
        getattr(input_arg, "project_id", None)
        or kwargs.get("project_id")
        or kwargs.get("id")
    )
    if not project_id:
        raise GraphQLError("Project ID가 필요합니다.")

    try:
        project = Project.objects.select_related("organization").get(pk=project_id)
    except Project.DoesNotExist:
        raise GraphQLError("Project를 찾을 수 없습니다.")

    return project


def _resolve_project_context(info, args, kwargs):
    """프로젝트와 조직 멤버십을 확인하고 info.context에 저장한다.

    인증 확인, 프로젝트 조회, 조직 멤버십 확인을 수행한다.
    Returns (project, org_membership) 튜플.
    """
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    project = _get_project(kwargs, args)
    org_membership = get_membership(user, project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.project = project
    info.context.membership = org_membership
    return project, org_membership


def project_access_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        project, org_membership = _resolve_project_context(info, args, kwargs)

        if not check_role(org_membership, Role.ADMIN):
            is_project_member = ProjectMembership.objects.filter(
                project=project, user=info.context.user
            ).exists()
            if not is_project_member:
                raise GraphQLError("이 프로젝트에 접근할 권한이 없습니다.")

        return func(root, info, *args, **kwargs)

    return wrapper


def project_admin_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        _, org_membership = _resolve_project_context(info, args, kwargs)

        if not check_role(org_membership, Role.ADMIN):
            raise GraphQLError("권한이 부족합니다.")

        return func(root, info, *args, **kwargs)

    return wrapper
