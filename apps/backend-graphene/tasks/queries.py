import graphene
from django.conf import settings
from django.db.models import Q

from projects.decorators import project_access_required
from tasks.decorators import task_access_required
from tasks.models import Task
from tasks.types import (
    PaginationInput,
    TaskConnectionType,
    TaskFilterInput,
    TaskType,
)


class TaskQuery(graphene.ObjectType):
    task = graphene.Field(TaskType, id=graphene.ID(required=True))
    tasks = graphene.Field(
        TaskConnectionType,
        project_id=graphene.ID(required=True),
        filter=TaskFilterInput(),
        pagination=PaginationInput(),
    )

    @task_access_required
    def resolve_task(root, info, id):
        return info.context.task

    @project_access_required
    def resolve_tasks(root, info, project_id, filter=None, pagination=None):
        qs = Task.objects.filter(task_group__board__project_id=project_id).order_by(
            "task_group__position", "position"
        )

        if filter:
            if filter.status:
                qs = qs.filter(status__in=filter.status)
            if filter.priority:
                qs = qs.filter(priority__in=filter.priority)
            if filter.assignee_id:
                qs = qs.filter(assignee_id=filter.assignee_id)
            if filter.due_date_from:
                qs = qs.filter(due_date__gte=filter.due_date_from)
            if filter.due_date_to:
                qs = qs.filter(due_date__lte=filter.due_date_to)
            if filter.search:
                qs = qs.filter(
                    Q(title__icontains=filter.search)
                    | Q(description__icontains=filter.search)
                )

        total_count = qs.count()

        limit = settings.GRAPHQL_PAGINATION_DEFAULT_LIMIT
        offset = 0
        if pagination:
            if pagination.limit is not None:
                max_limit = settings.GRAPHQL_PAGINATION_MAX_LIMIT
                limit = max(1, min(pagination.limit, max_limit))
            if pagination.offset is not None:
                offset = max(0, pagination.offset)

        tasks = qs[offset : offset + limit]
        has_next = (offset + limit) < total_count
        has_previous = offset > 0

        return TaskConnectionType(
            tasks=tasks,
            total_count=total_count,
            has_next=has_next,
            has_previous=has_previous,
        )
