from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Employee, Department, Skill, EmployeeSkill, PerformanceReview
from .serializers import EmployeeSerializer, DepartmentSerializer, SkillSerializer, EmployeeSkillSerializer, PerformanceReviewSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'position']
    ordering_fields = ['hire_date', 'salary', 'performance_score']

    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        top_employees = Employee.objects.annotate(
            avg_score=Avg('performance_reviews__score')
        ).order_by('-avg_score')[:10]
        serializer = self.get_serializer(top_employees, many=True)
        return Response(serializer.data)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    @action(detail=True, methods=['get'])
    def department_stats(self, request, pk=None):
        department = self.get_object()
        employee_count = department.employee_set.count()
        avg_salary = department.employee_set.aggregate(Avg('salary'))['salary__avg']
        return Response({
            'employee_count': employee_count,
            'average_salary': avg_salary
        })

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    @action(detail=True, methods=['get'])
    def employees_with_skill(self, request, pk=None):
        skill = self.get_object()
        employees = Employee.objects.filter(employeeskill__skill=skill)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['review_date', 'score']

    @action(detail=False, methods=['get'])
    def recent_reviews(self, request):
        recent_reviews = PerformanceReview.objects.order_by('-review_date')[:20]
        serializer = self.get_serializer(recent_reviews, many=True)
        return Response(serializer.data)