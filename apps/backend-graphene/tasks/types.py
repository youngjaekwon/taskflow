import graphene
from graphene_django import DjangoObjectType

from tasks.models import Task, TaskPriority, TaskStatus

TaskStatusEnum = graphene.Enum.from_enum(TaskStatus)
TaskPriorityEnum = graphene.Enum.from_enum(TaskPriority)


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "task_group",
            "position",
            "assignee",
            "due_date",
            "created_by",
            "created_at",
            "updated_at",
        ]


class TaskConnectionType(graphene.ObjectType):
    tasks = graphene.List(graphene.NonNull(TaskType))
    total_count = graphene.Int(required=True)
    has_next = graphene.Boolean(required=True)
    has_previous = graphene.Boolean(required=True)


# ── Input Types ──


class CreateTaskInput(graphene.InputObjectType):
    task_group_id = graphene.ID(required=True)
    title = graphene.String(required=True)
    description = graphene.String()
    status = TaskStatusEnum()
    priority = TaskPriorityEnum()
    assignee_id = graphene.ID()
    due_date = graphene.Date()


class UpdateTaskInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    title = graphene.String()
    description = graphene.String()
    status = TaskStatusEnum()
    priority = TaskPriorityEnum()
    due_date = graphene.Date()


class MoveTaskInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    target_task_group_id = graphene.ID(required=True)
    position = graphene.Int()


class ReorderTasksInput(graphene.InputObjectType):
    task_group_id = graphene.ID(required=True)
    task_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)


class AssignTaskInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    assignee_id = graphene.ID()


class TaskFilterInput(graphene.InputObjectType):
    status = graphene.List(TaskStatusEnum)
    priority = graphene.List(TaskPriorityEnum)
    assignee_id = graphene.ID()
    due_date_from = graphene.Date()
    due_date_to = graphene.Date()
    search = graphene.String()


class PaginationInput(graphene.InputObjectType):
    limit = graphene.Int()
    offset = graphene.Int()
