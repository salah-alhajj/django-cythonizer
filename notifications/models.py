from django.db import models

from projects.models import Project,Task
from employees.models import Employee

class Notification(models.Model):
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    related_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)


