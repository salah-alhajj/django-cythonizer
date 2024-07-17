from django.db import models
from employees.models import Employee
from projects.models import Task
from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import  MaxValueValidator

class TimeEntry(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    date = models.DateField()
    hours_worked = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(24)])
    description = models.TextField()

    class Meta:
        unique_together = ('employee', 'task', 'date')
