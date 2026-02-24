from functools import wraps

from graphql import GraphQLError

from labels.models import Label
from organizations.decorators import check_role, get_membership
from organizations.models import Role


def label_access_required(func):
    """Label에 대한 접근 권한을 확인한다.

    kwargs에서 id 또는 input.id로 Label ID를 추출하고,
    해당 Label이 속한 Organization의 ADMIN 이상 권한을 확인한다.
    """

    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("로그인이 필요합니다.")

        input_arg = kwargs.get("input") or (args[0] if args else None)
        label_id = getattr(input_arg, "id", None) or kwargs.get("id")
        if not label_id:
            raise GraphQLError("Label ID가 필요합니다.")

        try:
            label = Label.objects.select_related("organization").get(pk=label_id)
        except Label.DoesNotExist:
            raise GraphQLError("Label을 찾을 수 없습니다.")

        membership = get_membership(user, label.organization_id)
        if not membership:
            raise GraphQLError("이 Organization의 멤버가 아닙니다.")

        if not check_role(membership, Role.ADMIN):
            raise GraphQLError("권한이 부족합니다.")

        info.context.label = label
        info.context.membership = membership
        return func(root, info, *args, **kwargs)

    return wrapper
