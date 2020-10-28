from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class Member(AbstractBaseUser):
    is_training = models.BooleanField(default=False)


class Event(models.Model):
    class Type(models.IntegerChoices):
        TRAINED = 1
        RECOGNISED = 2

    team = models.ForeignKey(Member, on_delete=models.CASCADE)
    type = models.IntegerField(choices=Type.choices)
    score = models.FloatField(null=False)
    speed = models.FloatField()

    create_dttm = models.DateTimeField(auto_now_add=True)
