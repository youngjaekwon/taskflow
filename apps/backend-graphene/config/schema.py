import graphene

from boards.schema import BoardMutation, BoardQuery
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
    LabelMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
