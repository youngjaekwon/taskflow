import graphene
from django.db.models import F
from graphql import GraphQLError

from boards.models import TaskGroup
from graphql_utils import validate_fields
from projects.models import ProjectMembership
from tasks.decorators import (
    task_access_required,
    task_delete_permission_required,
    task_group_access_required,
)
from tasks.models import Task
from tasks.types import (
    AssignTaskInput,
    CreateTaskInput,
    MoveTaskInput,
    ReorderTasksInput,
    TaskType,
    UpdateTaskInput,
)


def _validate_assignee(assignee_id, project):
    if not ProjectMembership.objects.filter(
        project=project, user_id=assignee_id
    ).exists():
        raise GraphQLError("담당자는 프로젝트 멤버여야 합니다.")


# ── createTask ──


class CreateTask(graphene.Mutation):
    class Arguments:
        input = CreateTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_group_access_required
    def mutate(root, info, input):
        user = info.context.user
        project = info.context.project
        task_group = info.context.task_group

        assignee_id = input.assignee_id
        if assignee_id:
            _validate_assignee(assignee_id, project)

        max_position = (
            Task.objects.filter(task_group=task_group)
            .order_by("-position")
            .values_list("position", flat=True)
            .first()
        )
        new_position = 0 if max_position is None else max_position + 1

        data = {
            k: v
            for k, v in dict(input).items()
            if v is not None and k not in ("task_group_id", "assignee_id")
        }

        task = Task(
            task_group=task_group,
            position=new_position,
            created_by=user,
            **data,
        )
        if assignee_id:
            task.assignee_id = assignee_id

        validate_fields(task, data)
        task.save()
        return CreateTask(task=task)


# ── updateTask ──


class UpdateTask(graphene.Mutation):
    class Arguments:
        input = UpdateTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_access_required
    def mutate(root, info, input):
        task = info.context.task

        data = {
            k: v for k, v in dict(input).items() if v is not None and k != "task_id"
        }
        if not data:
            return UpdateTask(task=task)

        for field, value in data.items():
            setattr(task, field, value)

        validate_fields(task, data)
        task.save()
        return UpdateTask(task=task)


# ── deleteTask ──


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @task_delete_permission_required
    def mutate(root, info, id):
        task = info.context.task
        task_group_id = task.task_group_id
        deleted_position = task.position
        task.delete()
        Task.objects.filter(
            task_group_id=task_group_id,
            position__gt=deleted_position,
        ).update(position=F("position") - 1)
        return DeleteTask(success=True)


# ── moveTask ──


class MoveTask(graphene.Mutation):
    class Arguments:
        input = MoveTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_access_required
    def mutate(root, info, input):
        task = info.context.task
        current_board = task.task_group.board

        try:
            target_tg = TaskGroup.objects.select_related("board").get(
                pk=input.target_task_group_id
            )
        except TaskGroup.DoesNotExist:
            raise GraphQLError("대상 TaskGroup을 찾을 수 없습니다.")

        if target_tg.board_id != current_board.id:
            raise GraphQLError("같은 Board 내에서만 이동할 수 있습니다.")

        position = input.position
        if position is None:
            max_pos = (
                Task.objects.filter(task_group=target_tg)
                .order_by("-position")
                .values_list("position", flat=True)
                .first()
            )
            position = 0 if max_pos is None else max_pos + 1

        task.task_group = target_tg
        task.position = position
        task.save()
        return MoveTask(task=task)


# ── reorderTasks ──


class ReorderTasks(graphene.Mutation):
    class Arguments:
        input = ReorderTasksInput(required=True)

    tasks = graphene.List(graphene.NonNull(TaskType))

    @task_group_access_required
    def mutate(root, info, input):
        task_group = info.context.task_group
        task_ids = [int(tid) for tid in input.task_ids]

        if len(task_ids) != len(set(task_ids)):
            raise GraphQLError("중복된 Task ID가 포함되어 있습니다.")

        task_map = {t.id: t for t in Task.objects.filter(task_group=task_group)}

        if set(task_ids) != set(task_map):
            raise GraphQLError(
                "이 TaskGroup의 모든 Task ID를 빠짐없이 전달해야 합니다."
            )

        for position, tid in enumerate(task_ids):
            task_map[tid].position = position
        Task.objects.bulk_update(task_map.values(), ["position"])

        return ReorderTasks(tasks=[task_map[tid] for tid in task_ids])


# ── assignTask ──


class AssignTask(graphene.Mutation):
    class Arguments:
        input = AssignTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_access_required
    def mutate(root, info, input):
        task = info.context.task
        project = info.context.project

        assignee_id = input.assignee_id
        if assignee_id:
            _validate_assignee(assignee_id, project)
            task.assignee_id = assignee_id
        else:
            task.assignee = None

        task.save()
        return AssignTask(task=task)


class TaskMutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()
    move_task = MoveTask.Field()
    reorder_tasks = ReorderTasks.Field()
    assign_task = AssignTask.Field()
