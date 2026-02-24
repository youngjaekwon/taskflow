import pytest
from pytest_factoryboy import register

from boards.tests.factories import BoardFactory, TaskGroupFactory
from comments.tests.factories import CommentFactory
from organizations.models import OrganizationMembership, Role
from organizations.tests.factories import (
    OrganizationFactory,
    OrganizationMembershipFactory,
)
from projects.models import ProjectMembership
from projects.tests.factories import ProjectFactory, ProjectMembershipFactory
from tasks.tests.factories import TaskFactory

register(OrganizationFactory)
register(OrganizationMembershipFactory)
register(ProjectFactory)
register(ProjectMembershipFactory)
register(BoardFactory)
register(TaskGroupFactory)
register(TaskFactory)
register(CommentFactory)


@pytest.fixture
def org_with_owner(organization_factory, verified_user):
    org = organization_factory(created_by=verified_user)
    OrganizationMembership.objects.create(
        organization=org, user=verified_user, role=Role.OWNER
    )
    return org


@pytest.fixture
def project_with_member(project_factory, org_with_owner, verified_user):
    project = project_factory(organization=org_with_owner, created_by=verified_user)
    ProjectMembership.objects.create(
        project=project, user=verified_user, added_by=verified_user
    )
    return project


@pytest.fixture
def task_group_in_project(project_with_member):
    board = project_with_member.boards.first()
    return board.task_groups.first()


@pytest.fixture
def task_in_project(task_factory, task_group_in_project, verified_user):
    return task_factory(
        task_group=task_group_in_project,
        created_by=verified_user,
    )
