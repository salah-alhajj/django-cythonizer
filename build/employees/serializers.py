from rest_framework import serializers
from .models import Employee, Department, Skill, EmployeeSkill, PerformanceReview

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'skill', 'skill_name', 'proficiency_level']

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    skills = EmployeeSkillSerializer(source='employeeskill_set', many=True, read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'department', 'department_name', 'position', 'salary', 'hire_date', 'performance_score', 'skills']

class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.user.get_full_name', read_only=True)

    class Meta:
        model = PerformanceReview
        fields = ['id', 'employee', 'employee_name', 'reviewer', 'reviewer_name', 'review_date', 'score', 'comments', 'goals']