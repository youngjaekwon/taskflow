import graphene

from labels.models import Label
from labels.types import LabelType
from organizations.decorators import org_member_required


class LabelQuery(graphene.ObjectType):
    labels = graphene.List(
        graphene.NonNull(LabelType),
        organization_id=graphene.ID(required=True),
    )

    @org_member_required
    def resolve_labels(root, info, organization_id):
        return Label.objects.filter(organization_id=organization_id).order_by("name")
