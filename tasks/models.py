from django.db import models
from django.utils import timezone
from users.models import CustomUser


class Task(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открытая'),
        ('in_progress', 'В процессе выполнения'),
        ('closed', 'Закрытая / Выполненная'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title
