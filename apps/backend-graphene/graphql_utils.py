from django.core.exceptions import ValidationError as DjangoValidationError
from graphql import GraphQLError


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
