from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Sum
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from django.utils import timezone
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'budget']

    @action(detail=True, methods=['get'])
    def project_stats(self, request, pk=None):
        project = self.get_object()
        task_count = project.tasks.count()
        completed_tasks = project.tasks.filter(status='completed').count()
        total_hours = project.tasks.aggregate(Sum('estimated_hours'))['estimated_hours__sum']
        return Response({
            'task_count': task_count,
            'completed_tasks': completed_tasks,
            'total_estimated_hours': total_hours
        })

    @action(detail=False, methods=['get'])
    def top_budget_projects(self, request):
        top_projects = Project.objects.order_by('-budget')[:5]
        serializer = self.get_serializer(top_projects, many=True)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'status']

    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        overdue_tasks = Task.objects.filter(status__in=['not_started', 'in_progress'], due_date__lt=timezone.now().date())
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)