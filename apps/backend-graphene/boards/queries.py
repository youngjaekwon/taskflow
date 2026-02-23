import graphene

from boards.decorators import board_access_required
from boards.models import Board
from boards.types import BoardType
from projects.decorators import project_access_required


class BoardQuery(graphene.ObjectType):
    board = graphene.Field(BoardType, id=graphene.ID(required=True))
    boards = graphene.List(
        graphene.NonNull(BoardType),
        project_id=graphene.ID(required=True),
    )

    @board_access_required
    def resolve_board(root, info, id):
        return info.context.board

    @project_access_required
    def resolve_boards(root, info, project_id):
        return Board.objects.filter(project_id=project_id).order_by("created_at")
