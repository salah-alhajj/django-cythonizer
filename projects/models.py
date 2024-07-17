from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from employees.models import Employee,Department
class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    team_members = models.ManyToManyField(Employee, related_name='projects')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold')
    ])

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    due_date = models.DateTimeField()
    priority = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked')
    ])
    estimated_hours = models.FloatField()

    def __str__(self):
        return self.title
class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    achieved_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('delayed', 'Delayed')
    ])