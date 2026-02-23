from functools import wraps

from graphql import GraphQLError

from boards.models import Board
from organizations.decorators import check_role, get_membership
from organizations.models import Role
from projects.models import ProjectMembership


def _get_board(kwargs, args):
    input_arg = kwargs.get("input") or (args[0] if args else None)
    board_id = (
        getattr(input_arg, "board_id", None)
        or kwargs.get("board_id")
        or kwargs.get("id")
    )
    if not board_id:
        raise GraphQLError("Board ID가 필요합니다.")

    try:
        board = Board.objects.select_related("project__organization").get(pk=board_id)
    except Board.DoesNotExist:
        raise GraphQLError("Board를 찾을 수 없습니다.")

    return board


def _resolve_board_context(info, args, kwargs):
    user = info.context.user
    if not user.is_authenticated:
        raise GraphQLError("로그인이 필요합니다.")

    board = _get_board(kwargs, args)
    org_membership = get_membership(user, board.project.organization_id)
    if not org_membership:
        raise GraphQLError("이 Organization의 멤버가 아닙니다.")

    info.context.board = board
    info.context.project = board.project
    info.context.membership = org_membership
    return board, org_membership


def board_access_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        board, org_membership = _resolve_board_context(info, args, kwargs)

        if not check_role(org_membership, Role.ADMIN):
            is_project_member = ProjectMembership.objects.filter(
                project=board.project, user=info.context.user
            ).exists()
            if not is_project_member:
                raise GraphQLError("이 프로젝트에 접근할 권한이 없습니다.")

        return func(root, info, *args, **kwargs)

    return wrapper


def board_admin_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        _, org_membership = _resolve_board_context(info, args, kwargs)

        if not check_role(org_membership, Role.ADMIN):
            raise GraphQLError("권한이 부족합니다.")

        return func(root, info, *args, **kwargs)

    return wrapper
