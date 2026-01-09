from django.db import models

from users.models import User


class Status(models.Model):
    name = models.CharField(max_length=50)


class Task(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
