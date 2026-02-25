from promise import Promise
from promise.dataloader import DataLoader

from users.models import CustomUser


class UserByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        users = CustomUser.objects.in_bulk(int_keys)
        return Promise.resolve([users.get(int(k)) for k in keys])
