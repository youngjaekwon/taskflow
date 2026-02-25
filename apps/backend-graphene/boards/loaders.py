from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from boards.models import Board, TaskGroup


class BoardByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        boards = Board.objects.in_bulk(int_keys)
        return Promise.resolve([boards.get(int(k)) for k in keys])


class TaskGroupByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        task_groups = TaskGroup.objects.in_bulk(int_keys)
        return Promise.resolve([task_groups.get(int(k)) for k in keys])


class TaskGroupsByBoardLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        task_groups = TaskGroup.objects.filter(
            board_id__in=int_keys,
        ).order_by("position")

        grouped = defaultdict(list)
        for tg in task_groups:
            grouped[tg.board_id].append(tg)

        return Promise.resolve([grouped[int(k)] for k in keys])
