import graphene

from organizations.schema import OrganizationMutation, OrganizationQuery
from projects.schema import ProjectMutation, ProjectQuery
from users.schema import UserMutation, UserQuery


class Query(UserQuery, OrganizationQuery, ProjectQuery, graphene.ObjectType):
    pass


class Mutation(
    UserMutation, OrganizationMutation, ProjectMutation, graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
