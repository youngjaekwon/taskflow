import graphene
from graphene_django import DjangoObjectType

from boards.models import Board, TaskGroup


class TaskGroupType(DjangoObjectType):
    class Meta:
        model = TaskGroup
        fields = ["id", "name", "position", "created_at", "updated_at"]


class BoardType(DjangoObjectType):
    class Meta:
        model = Board
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "project",
            "created_by",
            "created_at",
            "updated_at",
        ]

    task_groups = graphene.List(graphene.NonNull(TaskGroupType))

    def resolve_task_groups(self, info):
        return self.task_groups.all()


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
