import graphene

from boards.schema import BoardMutation, BoardQuery
from comments.schema import CommentMutation, CommentQuery
from labels.schema import LabelMutation, LabelQuery
from organizations.schema import OrganizationMutation, OrganizationQuery
from projects.schema import ProjectMutation, ProjectQuery
from tasks.schema import TaskMutation, TaskQuery
from users.schema import UserMutation, UserQuery


class Query(
    UserQuery,
    OrganizationQuery,
    ProjectQuery,
    BoardQuery,
    TaskQuery,
    CommentQuery,
    LabelQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    UserMutation,
    OrganizationMutation,
    ProjectMutation,
    BoardMutation,
    TaskMutation,
    CommentMutation,
    LabelMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
