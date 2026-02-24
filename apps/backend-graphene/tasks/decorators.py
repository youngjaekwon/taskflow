from functools import wraps

from graphql import GraphQLError

from boards.models import TaskGroup
from organizations.decorators import check_role, get_membership
from organizations.models import Role
from projects.models import ProjectMembership
from tasks.models import Task

# ── helpers ──


def _check_project_access(org_membership, project, user):
    """프로젝트 접근 권한을 확인한다.

    Org ADMIN이면 True를 반환하고, 아니면 프로젝트 멤버십을 검증한다.
    프로젝트 멤버가 아니면 GraphQLError를 발생시킨다.

    Returns:
        bool: Org ADMIN 여부.
    """
    if check_role(org_membership, Role.ADMIN):
        return True

    is_project_member = ProjectMembership.objects.filter(
        project=project, user=user
    ).exists()
    if not is_project_member:
        raise GraphQLError("이 프로젝트에 접근할 권한이 없습니다.")

    return False


# ── Task Group context (for createTask, reorderTasks) ──


def _get_task_group(kwargs, args):
    input_arg = kwargs.get("input") or (args[0] if args else None)
    task_group_id = getattr(input_arg, "task_group_id", None) or kwargs.get(
        "task_group_id"
    )
    if not task_group_id:
        raise GraphQLError("TaskGroup ID가 필요합니다.")

    try:
        task_group = TaskGroup.objects.select_related(
            "board__project__organization"
        ).get(pk=task_group_id)
    except TaskGroup.DoesNotExist:
        raise GraphQLError("TaskGroup을 찾을 수 없습니다.")

    return task_group


def _resolve_task_group_context(info, args, kwargs):
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    task_group = _get_task_group(kwargs, args)
    project = task_group.board.project
    org_membership = get_membership(user, project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.task_group = task_group
    info.context.board = task_group.board
    info.context.project = project
    info.context.membership = org_membership
    return task_group, org_membership


def task_group_access_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        _, org_membership = _resolve_task_group_context(info, args, kwargs)
        _check_project_access(org_membership, info.context.project, info.context.user)
        return func(root, info, *args, **kwargs)

    return wrapper


# ── Task context (for updateTask, moveTask, assignTask, deleteTask) ──


def _get_task(kwargs, args):
    input_arg = kwargs.get("input") or (args[0] if args else None)
    task_id = (
        getattr(input_arg, "task_id", None) or kwargs.get("task_id") or kwargs.get("id")
    )
    if not task_id:
        raise GraphQLError("Task ID가 필요합니다.")

    try:
        task = Task.objects.select_related(
            "task_group__board__project__organization",
            "created_by",
        ).get(pk=task_id)
    except Task.DoesNotExist:
        raise GraphQLError("Task를 찾을 수 없습니다.")

    return task


def _resolve_task_context(info, args, kwargs):
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    task = _get_task(kwargs, args)
    project = task.task_group.board.project
    org_membership = get_membership(user, project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.task = task
    info.context.project = project
    info.context.membership = org_membership
    return task, org_membership


def task_access_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        _, org_membership = _resolve_task_context(info, args, kwargs)
        _check_project_access(org_membership, info.context.project, info.context.user)
        return func(root, info, *args, **kwargs)

    return wrapper


def task_delete_permission_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        task, org_membership = _resolve_task_context(info, args, kwargs)
        is_admin = _check_project_access(
            org_membership, info.context.project, info.context.user
        )

        if not is_admin and task.created_by_id != info.context.user.id:
            raise GraphQLError("Task 삭제 권한이 없습니다.")

        return func(root, info, *args, **kwargs)

    return wrapper
