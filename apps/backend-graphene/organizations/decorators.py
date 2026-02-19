from functools import wraps

from graphql import GraphQLError

from organizations.models import ROLE_HIERARCHY, OrganizationMembership


def get_membership(user, organization_id):
    try:
        return OrganizationMembership.objects.get(
            organization_id=organization_id, user=user
        )
    except OrganizationMembership.DoesNotExist:
        return None


def check_role(membership, min_role):
    return ROLE_HIERARCHY[membership.role] >= ROLE_HIERARCHY[min_role]


def org_member_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("로그인이 필요합니다.")

        input_arg = kwargs.get("input") or (args[0] if args else None)
        organization_id = (
            getattr(input_arg, "organization_id", None)
            or kwargs.get("organization_id")
            or kwargs.get("id")
        )
        if not organization_id:
            raise GraphQLError("Organization ID가 필요합니다.")

        membership = get_membership(user, organization_id)
        if not membership:
            raise GraphQLError("이 Organization의 멤버가 아닙니다.")

        info.context.membership = membership
        return func(root, info, *args, **kwargs)

    return wrapper


def org_role_required(min_role):
    def decorator(func):
        @wraps(func)
        def wrapper(root, info, *args, **kwargs):
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError("로그인이 필요합니다.")

            input_arg = kwargs.get("input") or (args[0] if args else None)
            organization_id = (
                getattr(input_arg, "organization_id", None)
                or kwargs.get("organization_id")
                or kwargs.get("id")
            )
            if not organization_id:
                raise GraphQLError("Organization ID가 필요합니다.")

            membership = get_membership(user, organization_id)
            if not membership:
                raise GraphQLError("이 Organization의 멤버가 아닙니다.")

            if not check_role(membership, min_role):
                raise GraphQLError("권한이 부족합니다.")

            info.context.membership = membership
            return func(root, info, *args, **kwargs)

        return wrapper

    return decorator
