import graphene

from organizations.schema import OrganizationMutation, OrganizationQuery
from users.schema import UserMutation, UserQuery


class Query(UserQuery, OrganizationQuery, graphene.ObjectType):
    pass


class Mutation(UserMutation, OrganizationMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
