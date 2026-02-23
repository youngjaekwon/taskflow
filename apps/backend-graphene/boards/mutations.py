import graphene
from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError

from boards.decorators import board_admin_required
from boards.models import Board, TaskGroup
from boards.types import (
    BoardType,
    CreateBoardInput,
    CreateTaskGroupInput,
    DeleteTaskGroupInput,
    ReorderTaskGroupsInput,
    TaskGroupType,
    UpdateBoardInput,
    UpdateTaskGroupInput,
)
from projects.decorators import project_admin_required


def _validate_fields(instance, field_names):
    exclude = [f.name for f in instance._meta.fields if f.name not in field_names]
    try:
        instance.clean_fields(exclude=exclude)
    except DjangoValidationError as e:
        messages = [msg for errors in e.message_dict.values() for msg in errors]
        raise GraphQLError("; ".join(messages))


def _get_task_group_for_board(task_group_id, board):
    try:
        task_group = TaskGroup.objects.get(pk=task_group_id)
    except TaskGroup.DoesNotExist:
        raise GraphQLError("TaskGroup을 찾을 수 없습니다.")

    if task_group.board_id != board.id:
        raise GraphQLError("TaskGroup을 찾을 수 없습니다.")

    return task_group


# ── Board CRUD ──


class CreateBoard(graphene.Mutation):
    class Arguments:
        input = CreateBoardInput(required=True)

    board = graphene.Field(BoardType)

    @project_admin_required
    def mutate(root, info, input):
        user = info.context.user

        data = {
            k: v for k, v in dict(input).items() if v is not None and k != "project_id"
        }

        board = Board(
            project_id=input.project_id,
            created_by=user,
            **data,
        )
        _validate_fields(board, data)
        board.save()
        return CreateBoard(board=board)


class UpdateBoard(graphene.Mutation):
    class Arguments:
        input = UpdateBoardInput(required=True)

    board = graphene.Field(BoardType)

    @board_admin_required
    def mutate(root, info, input):
        board = info.context.board

        data = {
            k: v for k, v in dict(input).items() if v is not None and k != "board_id"
        }
        if not data:
            return UpdateBoard(board=board)

        if "name" in data:
            board.slug = ""

        for field, value in data.items():
            setattr(board, field, value)

        _validate_fields(board, data)
        board.save()
        return UpdateBoard(board=board)


class DeleteBoard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @board_admin_required
    def mutate(root, info, id):
        board = info.context.board
        board.delete()
        return DeleteBoard(success=True)


# ── TaskGroup CRUD ──


class CreateTaskGroup(graphene.Mutation):
    class Arguments:
        input = CreateTaskGroupInput(required=True)

    task_group = graphene.Field(TaskGroupType)

    @board_admin_required
    def mutate(root, info, input):
        board = info.context.board

        max_position = (
            TaskGroup.objects.filter(board=board)
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )
        new_position = 0 if max_position is None else max_position + 1

        task_group = TaskGroup(
            name=input.name,
            board=board,
            position=new_position,
        )
        _validate_fields(task_group, ["name"])
        task_group.save()
        return CreateTaskGroup(task_group=task_group)


class UpdateTaskGroup(graphene.Mutation):
    class Arguments:
        input = UpdateTaskGroupInput(required=True)

    task_group = graphene.Field(TaskGroupType)

    @board_admin_required
    def mutate(root, info, input):
        task_group = _get_task_group_for_board(input.task_group_id, info.context.board)

        data = {
            k: v
            for k, v in dict(input).items()
            if v is not None and k not in ("task_group_id", "board_id")
        }
        if not data:
            return UpdateTaskGroup(task_group=task_group)

        for field, value in data.items():
            setattr(task_group, field, value)

        _validate_fields(task_group, data)
        task_group.save()
        return UpdateTaskGroup(task_group=task_group)


class DeleteTaskGroup(graphene.Mutation):
    class Arguments:
        input = DeleteTaskGroupInput(required=True)

    success = graphene.Boolean()

    @board_admin_required
    def mutate(root, info, input):
        task_group = _get_task_group_for_board(input.task_group_id, info.context.board)
        task_group.delete()
        return DeleteTaskGroup(success=True)


class ReorderTaskGroups(graphene.Mutation):
    class Arguments:
        input = ReorderTaskGroupsInput(required=True)

    task_groups = graphene.List(graphene.NonNull(TaskGroupType))

    @board_admin_required
    def mutate(root, info, input):
        board = info.context.board
        task_group_ids = [int(tg_id) for tg_id in input.task_group_ids]

        if len(task_group_ids) != len(set(task_group_ids)):
            raise GraphQLError("중복된 TaskGroup ID가 포함되어 있습니다.")

        tg_map = {tg.id: tg for tg in TaskGroup.objects.filter(board=board)}

        if set(task_group_ids) != set(tg_map):
            raise GraphQLError(
                "이 Board의 모든 TaskGroup ID를 빠짐없이 전달해야 합니다."
            )

        for position, tg_id in enumerate(task_group_ids):
            tg_map[tg_id].position = position
        TaskGroup.objects.bulk_update(tg_map.values(), ["position"])

        return ReorderTaskGroups(
            task_groups=[tg_map[tg_id] for tg_id in task_group_ids]
        )


class BoardMutation(graphene.ObjectType):
    create_board = CreateBoard.Field()
    update_board = UpdateBoard.Field()
    delete_board = DeleteBoard.Field()
    create_task_group = CreateTaskGroup.Field()
    update_task_group = UpdateTaskGroup.Field()
    delete_task_group = DeleteTaskGroup.Field()
    reorder_task_groups = ReorderTaskGroups.Field()
