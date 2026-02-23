import pytest

from boards.models import Board, TaskGroup


@pytest.mark.django_db
class TestBoardModel:
    def test_slug_auto_generated_from_name(self, board_factory, project_factory):
        project = project_factory()
        board = board_factory(name="My Board", project=project)
        assert board.slug == "my-board"

    def test_slug_unique_within_project(self, board_factory, project_factory):
        project = project_factory()
        b1 = board_factory(name="Duplicate", project=project)
        b2 = board_factory(name="Duplicate", project=project)
        assert b1.slug == "duplicate"
        assert b2.slug == "duplicate-2"

    def test_same_slug_allowed_in_different_projects(
        self, board_factory, project_factory
    ):
        p1 = project_factory()
        p2 = project_factory()
        b1 = board_factory(name="Same Name", project=p1)
        b2 = board_factory(name="Same Name", project=p2)
        assert b1.slug == "same-name"
        assert b2.slug == "same-name"

    def test_empty_name_slug_fallback(self, board_factory, project_factory):
        project = project_factory()
        board = board_factory(name="", project=project)
        assert board.slug == "board"

    def test_str(self, board_factory):
        board = board_factory(name="Test Board")
        assert str(board) == "Test Board"

    def test_cascade_delete_with_project(self, board_factory, project_factory):
        project = project_factory()
        project_id = project.pk
        board_factory(project=project)
        board_factory(project=project)
        # signal로 생성된 Main Board(1) + factory로 생성된 Board(2) = 3
        assert Board.objects.filter(project_id=project_id).count() == 3
        project.delete()
        assert Board.objects.filter(project_id=project_id).count() == 0


@pytest.mark.django_db
class TestTaskGroupModel:
    def test_default_position(self, task_group_factory, board_factory):
        board = board_factory()
        tg = task_group_factory(board=board)
        assert tg.position == 0

    def test_ordering_by_position(self, task_group_factory, board_factory):
        board = board_factory()
        tg3 = task_group_factory(board=board, position=2)
        tg1 = task_group_factory(board=board, position=0)
        tg2 = task_group_factory(board=board, position=1)
        result = list(TaskGroup.objects.filter(board=board))
        assert result == [tg1, tg2, tg3]

    def test_cascade_delete_with_board(self, task_group_factory, board_factory):
        board = board_factory()
        board_id = board.pk
        task_group_factory(board=board)
        task_group_factory(board=board)
        assert TaskGroup.objects.filter(board_id=board_id).count() == 2
        board.delete()
        assert TaskGroup.objects.filter(board_id=board_id).count() == 0

    def test_str(self, task_group_factory):
        tg = task_group_factory(name="To Do")
        assert str(tg) == "To Do"
