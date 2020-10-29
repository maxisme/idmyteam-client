from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Member(AbstractUser):
    class Permission(models.IntegerChoices):
        PHANTOM = 0, _('Phantom Member')
        CLASSIFY = 1, _('Classify Member')
        MEDIUM = 2, _('Medium Member')
        HIGH = 3, _('High Member')

    is_training = models.BooleanField(default=False)
    permission = models.PositiveSmallIntegerField(choices=Permission.choices, null=False)


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
    Member.Permission.CLASSIFY: "Allowed to classify and view team members.",
    Member.Permission.MEDIUM: "Allowed to add new members, delete member classification, view the live stream and customise the script.",
    Member.Permission.HIGH: "Allowed to choose member permissions, delete team members, view the logs and customise the settings.",
}
