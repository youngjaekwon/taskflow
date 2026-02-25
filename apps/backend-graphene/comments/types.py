import graphene
from graphene_django import DjangoObjectType

from comments.models import Comment


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "created_at",
            "updated_at",
        ]

    task = graphene.Field("tasks.types.TaskType")
    parent = graphene.Field(lambda: CommentType)
    author = graphene.Field("users.types.UserType")
    replies = graphene.List(graphene.NonNull(lambda: CommentType))

    def resolve_task(self, info):
        return info.context.task_by_id_loader.load(self.task_id)

    def resolve_parent(self, info):
        if self.parent_id is None:
            return None
        return info.context.comment_by_id_loader.load(self.parent_id)

    def resolve_author(self, info):
        if self.author_id is None:
            return None
        return info.context.user_by_id_loader.load(self.author_id)

    def resolve_replies(self, info):
        return info.context.replies_by_comment_loader.load(self.id)


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
