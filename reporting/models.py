from django.db import models

from projects.models import Project
from employees.models import Employee

class Report(models.Model):
    title = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='approved_reports')

