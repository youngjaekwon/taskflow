from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from projects.models import Project, ProjectMembership


class ProjectByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        projects = Project.objects.in_bulk(int_keys)
        return Promise.resolve([projects.get(int(k)) for k in keys])


class MembershipsByProjectLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        memberships = ProjectMembership.objects.filter(
            project_id__in=int_keys,
        )

        grouped = defaultdict(list)
        for m in memberships:
            grouped[m.project_id].append(m)

        return Promise.resolve([grouped[int(k)] for k in keys])
