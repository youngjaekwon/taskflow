from django.db.models.signals import post_save
from django.dispatch import receiver

from boards.models import Board, TaskGroup
from projects.models import Project

DEFAULT_TASK_GROUPS = [
    ("To Do", 0),
    ("In Progress", 1),
    ("In Review", 2),
    ("Done", 3),
]


@receiver(post_save, sender=Project)
def create_default_board(sender, instance, created, **kwargs):
    if not created:
        return

    board = Board.objects.create(
        name="Main Board",
        project=instance,
        created_by=instance.created_by,
    )

    TaskGroup.objects.bulk_create(
        [
            TaskGroup(name=name, board=board, position=position)
            for name, position in DEFAULT_TASK_GROUPS
        ]
    )
