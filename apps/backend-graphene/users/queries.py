import graphene

from users.decorators import login_required
from users.types import UserType


class UserQuery(graphene.ObjectType):
    me = graphene.Field(UserType)

    @login_required
    def resolve_me(root, info):
        return info.context.user
