import graphene
from graphql import GraphQLError

from comments.decorators import comment_author_required, comment_task_access_required
from comments.models import Comment
from comments.types import CommentType, CreateCommentInput, UpdateCommentInput

# ── createComment ──


class CreateComment(graphene.Mutation):
    class Arguments:
        input = CreateCommentInput(required=True)

    comment = graphene.Field(CommentType)

    @comment_task_access_required
    def mutate(root, info, input):
        user = info.context.user
        task = info.context.task

        parent = None
        if input.parent_id:
            try:
                parent = Comment.objects.get(pk=input.parent_id)
            except Comment.DoesNotExist:
                raise GraphQLError("부모 댓글을 찾을 수 없습니다.")

            if parent.task_id != task.id:
                raise GraphQLError("부모 댓글은 같은 Task에 속해야 합니다.")

            if parent.parent_id is not None:
                raise GraphQLError("1단계 대댓글만 허용됩니다.")

        content = input.content
        if not content or not content.strip():
            raise GraphQLError("댓글 내용을 입력해주세요.")

        comment = Comment(
            content=content,
            task=task,
            parent=parent,
            author=user,
        )
        comment.save()
        return CreateComment(comment=comment)


# ── updateComment ──


class UpdateComment(graphene.Mutation):
    class Arguments:
        input = UpdateCommentInput(required=True)

    comment = graphene.Field(CommentType)

    @comment_author_required
    def mutate(root, info, input):
        comment = info.context.comment

        content = input.content
        if not content or not content.strip():
            raise GraphQLError("댓글 내용을 입력해주세요.")

        comment.content = content
        comment.save()
        return UpdateComment(comment=comment)


# ── deleteComment ──


class DeleteComment(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    @comment_author_required
    def mutate(root, info, id):
        comment = info.context.comment
        comment.delete()
        return DeleteComment(success=True)


class CommentMutation(graphene.ObjectType):
    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()
