from graphene_django.views import GraphQLView
from graphql_core_promise import PromiseExecutionContext

from config.context import GQLContext


class CustomGraphQLView(GraphQLView):
    execution_context_class = PromiseExecutionContext

    def get_context(self, request):
        return GQLContext(request)
