import graphene
from graphene_django import DjangoObjectType

from boards.models import Board, TaskGroup


class TaskGroupType(DjangoObjectType):
    class Meta:
        model = TaskGroup
        fields = ["id", "name", "position", "created_at", "updated_at"]

    tasks = graphene.List(graphene.NonNull("tasks.types.TaskType"))

    def resolve_tasks(self, info):
        return info.context.tasks_by_task_group_loader.load(self.id)


class BoardType(DjangoObjectType):
    class Meta:
        model = Board
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created_at",
            "updated_at",
        ]

    project = graphene.Field("projects.types.ProjectType")
    created_by = graphene.Field("users.types.UserType")
    task_groups = graphene.List(graphene.NonNull(TaskGroupType))

    def resolve_project(self, info):
        return info.context.project_by_id_loader.load(self.project_id)

    def resolve_created_by(self, info):
        if self.created_by_id is None:
            return None
        return info.context.user_by_id_loader.load(self.created_by_id)

    def resolve_task_groups(self, info):
        return info.context.task_groups_by_board_loader.load(self.id)


# ── Input Types ──


class CreateBoardInput(graphene.InputObjectType):
    project_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()


class UpdateBoardInput(graphene.InputObjectType):
    board_id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()


class CreateTaskGroupInput(graphene.InputObjectType):
    board_id = graphene.ID(required=True)
    name = graphene.String(required=True)


class UpdateTaskGroupInput(graphene.InputObjectType):
    board_id = graphene.ID(required=True)
    task_group_id = graphene.ID(required=True)
    name = graphene.String()


class DeleteTaskGroupInput(graphene.InputObjectType):
    board_id = graphene.ID(required=True)
    task_group_id = graphene.ID(required=True)


class ReorderTaskGroupsInput(graphene.InputObjectType):
    board_id = graphene.ID(required=True)
    task_group_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
