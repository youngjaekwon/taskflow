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
            "created_at",
            "updated_at",
        ]

    organization = graphene.Field("organizations.types.OrganizationType")
    created_by = graphene.Field("users.types.UserType")

    def resolve_organization(self, info):
        return info.context.organization_by_id_loader.load(self.organization_id)

    def resolve_created_by(self, info):
        if self.created_by_id is None:
            return None
        return info.context.user_by_id_loader.load(self.created_by_id)


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
