import graphene

from boards.schema import BoardMutation, BoardQuery
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
    graphene.ObjectType,
):
    pass


class Mutation(
    UserMutation,
    OrganizationMutation,
    ProjectMutation,
    BoardMutation,
    TaskMutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
