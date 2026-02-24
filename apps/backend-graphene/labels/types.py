import graphene
from graphene_django import DjangoObjectType

from labels.models import Label


class LabelType(DjangoObjectType):
    class Meta:
        model = Label
        fields = [
            "id",
            "name",
            "color",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
        ]


# ── Input Types ──


class CreateLabelInput(graphene.InputObjectType):
    organization_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    color = graphene.String()


class UpdateLabelInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    name = graphene.String()
    color = graphene.String()


class AddLabelsToTaskInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    label_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)


class RemoveLabelsFromTaskInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    label_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
