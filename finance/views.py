from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'project__name', 'employee__user__first_name', 'employee__user__last_name']
    ordering_fields = ['date', 'amount', 'status']

    @action(detail=False, methods=['get'])
    def total_expenses(self, request):
        total = Expense.objects.aggregate(Sum('amount'))['amount__sum']
        return Response({'total_expenses': total})

    @action(detail=False, methods=['get'])
    def expenses_by_status(self, request):
        expenses = Expense.objects.values('status').annotate(total=Sum('amount'))
        return Response(expenses)