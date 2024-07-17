from django.contrib import admin
from .models import*
admin.site.register([Employee,Department,Skill,EmployeeSkill,PerformanceReview])
