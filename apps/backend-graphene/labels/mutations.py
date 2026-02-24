import graphene
from django.db import IntegrityError
from graphql import GraphQLError

from graphql_utils import validate_fields
from labels.decorators import label_access_required
from labels.models import Label
from labels.types import (
    AddLabelsToTaskInput,
    CreateLabelInput,
    LabelType,
    RemoveLabelsFromTaskInput,
    UpdateLabelInput,
)
from organizations.decorators import org_role_required
from organizations.models import Role
from tasks.decorators import task_access_required
from tasks.types import TaskType

# ── createLabel ──


class CreateLabel(graphene.Mutation):
    class Arguments:
        input = CreateLabelInput(required=True)

    label = graphene.Field(LabelType)

    @org_role_required(Role.ADMIN)
    def mutate(root, info, input):
        user = info.context.user

        if not input.name.strip():
            raise GraphQLError("Label 이름은 비어있을 수 없습니다.")

        data = {"name": input.name.strip()}
        if input.color is not None:
            data["color"] = input.color

        label = Label(
            organization_id=input.organization_id,
            created_by=user,
            **data,
        )
        validate_fields(label, data)

        try:
            label.save()
        except IntegrityError:
            raise GraphQLError("이미 같은 이름의 Label이 존재합니다.")

        return CreateLabel(label=label)


# ── updateLabel ──


class UpdateLabel(graphene.Mutation):
    class Arguments:
        input = UpdateLabelInput(required=True)

    label = graphene.Field(LabelType)

    @label_access_required
    def mutate(root, info, input):
        label = info.context.label

        data = {k: v for k, v in dict(input).items() if v is not None and k != "id"}
        if not data:
            return UpdateLabel(label=label)

        for field, value in data.items():
            setattr(label, field, value)

        validate_fields(label, data)

        try:
            label.save()
        except IntegrityError:
            raise GraphQLError("이미 같은 이름의 Label이 존재합니다.")

        return UpdateLabel(label=label)


# ── deleteLabel ──


class DeleteLabel(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @label_access_required
    def mutate(root, info, id):
        label = info.context.label
        label.delete()
        return DeleteLabel(success=True)


# ── addLabelsToTask ──


class AddLabelsToTask(graphene.Mutation):
    class Arguments:
        input = AddLabelsToTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_access_required
    def mutate(root, info, input):
        task = info.context.task
        project = info.context.project
        org_id = project.organization_id

        labels = Label.objects.filter(pk__in=input.label_ids)
        if labels.count() != len(input.label_ids):
            raise GraphQLError("존재하지 않는 Label이 포함되어 있습니다.")
        if labels.exclude(organization_id=org_id).exists():
            raise GraphQLError("다른 Organization의 Label은 추가할 수 없습니다.")

        task.labels.add(*labels)
        return AddLabelsToTask(task=task)


# ── removeLabelsFromTask ──


class RemoveLabelsFromTask(graphene.Mutation):
    class Arguments:
        input = RemoveLabelsFromTaskInput(required=True)

    task = graphene.Field(TaskType)

    @task_access_required
    def mutate(root, info, input):
        task = info.context.task
        task.labels.remove(*input.label_ids)
        return RemoveLabelsFromTask(task=task)


class LabelMutation(graphene.ObjectType):
    create_label = CreateLabel.Field()
    update_label = UpdateLabel.Field()
    delete_label = DeleteLabel.Field()
    add_labels_to_task = AddLabelsToTask.Field()
    remove_labels_from_task = RemoveLabelsFromTask.Field()
