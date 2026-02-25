from functools import cached_property

from boards.loaders import BoardByIdLoader, TaskGroupByIdLoader, TaskGroupsByBoardLoader
from comments.loaders import CommentByIdLoader, RepliesByCommentLoader
from labels.loaders import LabelByIdLoader, LabelsByTaskLoader
from organizations.loaders import (
    MembershipsByOrganizationLoader,
    OrganizationByIdLoader,
)
from projects.loaders import MembershipsByProjectLoader, ProjectByIdLoader
from tasks.loaders import (
    CommentCountByTaskLoader,
    TaskByIdLoader,
    TasksByTaskGroupLoader,
)
from users.loaders import UserByIdLoader


class GQLContext:
    def __init__(self, request):
        self.request = request

    def __getattr__(self, name):
        return getattr(self.request, name)

    @property
    def user(self):
        return self.request.user

    # ── Users ──

    @cached_property
    def user_by_id_loader(self):
        return UserByIdLoader()

    # ── Organizations ──

    @cached_property
    def organization_by_id_loader(self):
        return OrganizationByIdLoader()

    @cached_property
    def memberships_by_organization_loader(self):
        return MembershipsByOrganizationLoader()

    # ── Projects ──

    @cached_property
    def project_by_id_loader(self):
        return ProjectByIdLoader()

    @cached_property
    def memberships_by_project_loader(self):
        return MembershipsByProjectLoader()

    # ── Boards ──

    @cached_property
    def board_by_id_loader(self):
        return BoardByIdLoader()

    @cached_property
    def task_group_by_id_loader(self):
        return TaskGroupByIdLoader()

    @cached_property
    def task_groups_by_board_loader(self):
        return TaskGroupsByBoardLoader()

    # ── Tasks ──

    @cached_property
    def task_by_id_loader(self):
        return TaskByIdLoader()

    @cached_property
    def tasks_by_task_group_loader(self):
        return TasksByTaskGroupLoader()

    @cached_property
    def comment_count_by_task_loader(self):
        return CommentCountByTaskLoader()

    # ── Comments ──

    @cached_property
    def comment_by_id_loader(self):
        return CommentByIdLoader()

    @cached_property
    def replies_by_comment_loader(self):
        return RepliesByCommentLoader()

    # ── Labels ──

    @cached_property
    def label_by_id_loader(self):
        return LabelByIdLoader()

    @cached_property
    def labels_by_task_loader(self):
        return LabelsByTaskLoader()
