import graphene
from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError

from users.decorators import login_required
from users.types import UserType


class UpdateProfileInput(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()


class UpdateProfile(graphene.Mutation):
    class Arguments:
        input = UpdateProfileInput(required=True)

    user = graphene.Field(UserType)

    @login_required
    def mutate(root, info, input):
        user = info.context.user
        data = {k: v for k, v in dict(input).items() if v is not None}
        if not data:
            return UpdateProfile(user=user)

        for field, value in data.items():
            setattr(user, field, value)

        exclude = [f.name for f in user._meta.fields if f.name not in data]
        try:
            user.clean_fields(exclude=exclude)
        except DjangoValidationError as e:
            messages = []
            for field, errors in e.message_dict.items():
                messages.extend(errors)
            raise GraphQLError("; ".join(messages))

        user.save(update_fields=list(data.keys()))
        return UpdateProfile(user=user)


class UserMutation(graphene.ObjectType):
    update_profile = UpdateProfile.Field()
