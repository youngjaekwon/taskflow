from collections import defaultdict

from promise import Promise
from promise.dataloader import DataLoader

from organizations.models import Organization, OrganizationMembership


class OrganizationByIdLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        orgs = Organization.objects.in_bulk(int_keys)
        return Promise.resolve([orgs.get(int(k)) for k in keys])


class MembershipsByOrganizationLoader(DataLoader):
    def batch_load_fn(self, keys):
        int_keys = [int(k) for k in keys]
        memberships = OrganizationMembership.objects.filter(
            organization_id__in=int_keys,
        )

        grouped = defaultdict(list)
        for m in memberships:
            grouped[m.organization_id].append(m)

        return Promise.resolve([grouped[int(k)] for k in keys])
