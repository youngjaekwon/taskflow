from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from comments.models import Comment


class CommentByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        comments = Comment.objects.in_bulk(int_keys)
        return Promise.resolve([comments.get(int(k)) for k in keys])


class RepliesByCommentLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        replies = Comment.objects.filter(
            parent_id__in=int_keys,
        ).order_by("created_at")

        grouped = defaultdict(list)
        for reply in replies:
            grouped[reply.parent_id].append(reply)

        return Promise.resolve([grouped[int(k)] for k in keys])
