from django.urls import path, include
from rest_framework import routers
from .views import EmployeeViewSet, DepartmentViewSet, department_employee_chart

router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'departments', DepartmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('charts/departments/', department_employee_chart, name='department-chart'),
]


# API v1 extraction endpoints
from .views import health, scan_start, scan_status, scan_result, scan_cancel, scan_remove, jobs_list, jobs_statistics

urlpatterns += [
    path('v1/health', health, name='health'),
    path('v1/scan/start', scan_start, name='scan-start'),
    path('v1/scan/status/<uuid:job_id>', scan_status, name='scan-status'),
    path('v1/scan/result/<uuid:job_id>', scan_result, name='scan-result'),
    path('v1/scan/cancel/<uuid:job_id>', scan_cancel, name='scan-cancel'),
    path('v1/scan/remove/<uuid:job_id>', scan_remove, name='scan-remove'),
    path('v1/jobs/jobs', jobs_list, name='jobs-list'),
    path('v1/jobs/statistics', jobs_statistics, name='jobs-statistics'),
]
