from functools import wraps

from graphql import GraphQLError


def login_required(func):
    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("로그인이 필요합니다.")
        return func(root, info, *args, **kwargs)

    return wrapper
