from functools import wraps

from graphql import GraphQLError

from comments.models import Comment
from organizations.decorators import get_membership
from tasks.decorators import _check_project_access
from tasks.models import Task


def _resolve_comment_task_context(info, kwargs, args):
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    input_arg = kwargs.get("input") or (args[0] if args else None)
    task_id = getattr(input_arg, "task_id", None) or kwargs.get("task_id")
    if not task_id:
        raise GraphQLError("Task ID가 필요합니다.")

    try:
        task = Task.objects.select_related(
            "task_group__board__project__organization",
        ).get(pk=task_id)
    except Task.DoesNotExist:
        raise GraphQLError("Task를 찾을 수 없습니다.")

    project = task.task_group.board.project
    org_membership = get_membership(user, project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.task = task
    info.context.project = project
    info.context.membership = org_membership
    return task, org_membership


def comment_task_access_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        _, org_membership = _resolve_comment_task_context(info, kwargs, args)
        _check_project_access(org_membership, info.context.project, info.context.user)
        return func(root, info, *args, **kwargs)

    return wrapper


def _resolve_comment_context(info, kwargs, args):
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    input_arg = kwargs.get("input") or (args[0] if args else None)
    comment_id = (
        getattr(input_arg, "comment_id", None)
        or kwargs.get("comment_id")
        or kwargs.get("id")
    )
    if not comment_id:
        raise GraphQLError("Comment ID가 필요합니다.")

    try:
        comment = Comment.objects.select_related(
            "task__task_group__board__project__organization",
            "author",
        ).get(pk=comment_id)
    except Comment.DoesNotExist:
        raise GraphQLError("Comment를 찾을 수 없습니다.")

    task = comment.task
    project = task.task_group.board.project
    org_membership = get_membership(user, project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.comment = comment
    info.context.task = task
    info.context.project = project
    info.context.membership = org_membership
    return comment, org_membership


def comment_author_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        comment, org_membership = _resolve_comment_context(info, kwargs, args)
        _check_project_access(org_membership, info.context.project, info.context.user)

        if comment.author_id != info.context.user.id:
            raise GraphQLError("댓글 작성자만 수정/삭제할 수 있습니다.")

        return func(root, info, *args, **kwargs)

    return wrapper
