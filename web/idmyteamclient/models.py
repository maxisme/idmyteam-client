from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

PERMISSION_NAMES = {
    "phantom": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


class Member(AbstractUser):
    UNKNOWN_NAME = "UNKNOWN"

    class Permission(models.IntegerChoices):
        PHANTOM = PERMISSION_NAMES["phantom"], _("Phantom Member")
        LOW = PERMISSION_NAMES["low"], _("Low Member")
        MEDIUM = PERMISSION_NAMES["medium"], _("Medium Member")
        HIGH = PERMISSION_NAMES["high"], _("High Member")

    is_training = models.BooleanField(default=False)
    permission = models.PositiveSmallIntegerField(
        choices=Permission.choices, null=False
    )

    def permitted(self, perm) -> bool:
        if isinstance(perm, str):
            if perm not in PERMISSION_NAMES:
                raise Exception(f"Invalid permission name '{perm}'")
            perm = PERMISSION_NAMES[perm]

        return self.permission >= perm

    @property
    def num_trained(self):
        return len(Event.objects.filter(team_id=self.id, type=Event.Type.TRAINED))

    @property
    def num_recognitions(self):
        return len(Event.objects.filter(team_id=self.id, type=Event.Type.RECOGNISED))


class Event(models.Model):
    class Type(models.IntegerChoices):
        TRAINED = 1
        RECOGNISED = 2

    team = models.ForeignKey(Member, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=Type.choices, null=False)
    score = models.FloatField(null=False)
    speed = models.FloatField()

    create_dttm = models.DateTimeField(auto_now_add=True)


PERMISSION_DESCRIPTIONS = {
    Member.Permission.PHANTOM: "No access to web panel. - Only used for recognitions.",
    Member.Permission.LOW: "Allowed to classify and view team members.",
    Member.Permission.MEDIUM: "Allowed to add new members, delete member classification and customise the script.",
    Member.Permission.HIGH: "Allowed to choose member permissions, delete team members, view the live stream camera, view the logs and customise the settings.",
}
