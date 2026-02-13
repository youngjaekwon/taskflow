import graphene
from graphene_django import DjangoObjectType

from users.models import CustomUser


class UserType(DjangoObjectType):
    profile_image = graphene.String()

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

    def resolve_profile_image(self, info):
        if not self.profile_image:
            return None
        return info.context.build_absolute_uri(self.profile_image.url)
