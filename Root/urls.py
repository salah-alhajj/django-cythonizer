
from django.contrib import admin
from django.urls import path ,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/employees/', include('employees.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/finance/', include('finance.urls'))
]