from collections import defaultdict

from django.db.models import Count
from promise import Promise
from promise.dataloader import DataLoader

from comments.models import Comment
from tasks.models import Task


class TaskByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        tasks = Task.objects.in_bulk(int_keys)
        return Promise.resolve([tasks.get(int(k)) for k in keys])


class TasksByTaskGroupLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        tasks = Task.objects.filter(
            task_group_id__in=int_keys,
        ).order_by("position")

        grouped = defaultdict(list)
        for task in tasks:
            grouped[task.task_group_id].append(task)

        return Promise.resolve([grouped[int(k)] for k in keys])


class CommentCountByTaskLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        counts = dict(
            Comment.objects.filter(task_id__in=int_keys)
            .values_list("task_id")
            .annotate(count=Count("id"))
            .values_list("task_id", "count")
        )
        return Promise.resolve([counts.get(int(k), 0) for k in keys])
