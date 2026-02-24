import graphene
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError


class PaginationInput(graphene.InputObjectType):
    limit = graphene.Int()
    offset = graphene.Int()


def apply_pagination(queryset, pagination):
    """QuerySet에 페이지네이션을 적용한다.

    Returns:
        (items, total_count, has_next, has_previous)
    """
    total_count = queryset.count()

    limit = settings.GRAPHQL_PAGINATION_DEFAULT_LIMIT
    offset = 0
    if pagination:
        if pagination.limit is not None:
            max_limit = settings.GRAPHQL_PAGINATION_MAX_LIMIT
            limit = max(1, min(pagination.limit, max_limit))
        if pagination.offset is not None:
            offset = max(0, pagination.offset)

    items = queryset[offset : offset + limit]
    has_next = (offset + limit) < total_count
    has_previous = offset > 0

    return items, total_count, has_next, has_previous


def validate_fields(instance, field_names):
    """지정된 필드에 대해 Django 모델 검증을 실행한다.

    검증 실패 시 GraphQLError를 발생시킨다.
    """
    exclude = [f.name for f in instance._meta.fields if f.name not in field_names]
    try:
        instance.clean_fields(exclude=exclude)
    except DjangoValidationError as e:
        messages = [msg for errors in e.message_dict.values() for msg in errors]
        raise GraphQLError("; ".join(messages))
