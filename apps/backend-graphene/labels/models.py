from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Label(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(
        max_length=7,
        default="#808080",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="색상은 #RRGGBB 형식이어야 합니다.",
            ),
        ],
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="labels",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_labels",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name
