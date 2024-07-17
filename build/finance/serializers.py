from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'project', 'project_name', 'employee', 'employee_name', 'amount', 'date', 'description', 'status']