from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from labels.models import Label
from tasks.models import Task


class LabelByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        labels = Label.objects.in_bulk(int_keys)
        return Promise.resolve([labels.get(int(k)) for k in keys])


class LabelsByTaskLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        through_model = Task.labels.through
        rows = through_model.objects.filter(
            task_id__in=int_keys,
        ).select_related("label")

        grouped = defaultdict(list)
        for row in rows:
            grouped[row.task_id].append(row.label)

        return Promise.resolve([grouped[int(k)] for k in keys])
