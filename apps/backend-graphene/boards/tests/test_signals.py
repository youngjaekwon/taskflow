import pytest

from boards.models import Board, TaskGroup


@pytest.mark.django_db
class TestDefaultBoardCreation:
    def test_project_creation_creates_default_board(
        self, project_factory, organization_factory, verified_user
    ):
        org = organization_factory()
        project = project_factory(organization=org, created_by=verified_user)
        boards = Board.objects.filter(project=project)
        assert boards.count() == 1
        board = boards.first()
        assert board.name == "Main Board"
        assert board.created_by == verified_user

    def test_project_creation_creates_four_task_groups(
        self, project_factory, organization_factory, verified_user
    ):
        org = organization_factory()
        project = project_factory(organization=org, created_by=verified_user)
        board = Board.objects.get(project=project)
        task_groups = list(TaskGroup.objects.filter(board=board).order_by("position"))
        assert len(task_groups) == 4
        assert task_groups[0].name == "To Do"
        assert task_groups[0].position == 0
        assert task_groups[1].name == "In Progress"
        assert task_groups[1].position == 1
        assert task_groups[2].name == "In Review"
        assert task_groups[2].position == 2
        assert task_groups[3].name == "Done"
        assert task_groups[3].position == 3

    def test_task_group_created_by_matches_project_created_by(
        self, project_factory, organization_factory, verified_user
    ):
        org = organization_factory()
        project = project_factory(organization=org, created_by=verified_user)
        board = Board.objects.get(project=project)
        assert board.created_by == project.created_by

    def test_project_update_does_not_create_additional_board(
        self, project_factory, organization_factory, verified_user
    ):
        org = organization_factory()
        project = project_factory(organization=org, created_by=verified_user)
        assert Board.objects.filter(project=project).count() == 1
        project.name = "Updated Name"
        project.save()
        assert Board.objects.filter(project=project).count() == 1
