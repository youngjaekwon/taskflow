import graphene
from graphene_django import DjangoObjectType

from comments.models import Comment


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "task",
            "parent",
            "author",
            "created_at",
            "updated_at",
        ]

    replies = graphene.List(graphene.NonNull(lambda: CommentType))

    def resolve_replies(self, info):
        return self.replies.all()


class CommentConnectionType(graphene.ObjectType):
    comments = graphene.List(graphene.NonNull(CommentType))
    total_count = graphene.Int(required=True)
    has_next = graphene.Boolean(required=True)
    has_previous = graphene.Boolean(required=True)


# ── Input Types ──


class CreateCommentInput(graphene.InputObjectType):
    task_id = graphene.ID(required=True)
    content = graphene.String(required=True)
    parent_id = graphene.ID()


class UpdateCommentInput(graphene.InputObjectType):
    comment_id = graphene.ID(required=True)
    content = graphene.String(required=True)
