import graphene

from comments.decorators import comment_task_access_required
from comments.models import Comment
from comments.types import CommentConnectionType
from graphql_utils import PaginationInput, apply_pagination


class CommentQuery(graphene.ObjectType):
    comments = graphene.Field(
        CommentConnectionType,
        task_id=graphene.ID(required=True),
        pagination=PaginationInput(),
    )

    @comment_task_access_required
    def resolve_comments(root, info, task_id, pagination=None):
        qs = Comment.objects.filter(task_id=task_id, parent__isnull=True)

        comments, total_count, has_next, has_previous = apply_pagination(qs, pagination)

        return CommentConnectionType(
            comments=comments,
            total_count=total_count,
            has_next=has_next,
            has_previous=has_previous,
        )
