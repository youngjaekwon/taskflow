from graphene_django import DjangoObjectType

from users.models import CustomUser


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "email_verified",
            "profile_image",
            "date_joined",
        ]
