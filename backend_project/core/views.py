from rest_framework import viewsets
from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer

# Existing DRF viewsets
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# New function-based view for chart
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io

def department_employee_chart(request):
    fig, ax = plt.subplots()
    
    departments = Department.objects.all()
    names = [d.name for d in departments]
    counts = [d.employees.count() for d in departments]
    
    ax.bar(names, counts)
    ax.set_ylabel("Number of Employees")
    ax.set_title("Employees per Department")
    
    # Save figure to a bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    return HttpResponse(buf.getvalue(), content_type='image/png')


# Extraction API views (simple implementations)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as http_status
from .models import ExtractionJob, ExtractedRecord
from .serializers import ExtractionJobSerializer, ExtractedRecordSerializer


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'})


@api_view(['POST'])
def scan_start(request):
    # Expecting {'api_token': '...'} in body. We'll create a job and simulate async behavior.
    api_token = request.data.get('api_token', '')
    if not api_token:
        return Response({'detail': 'api_token is required'}, status=http_status.HTTP_400_BAD_REQUEST)
    job = ExtractionJob.objects.create(api_token=api_token)
    # For now, mark in progress and immediately create zero records as a simple seeded behavior.
    job.mark_in_progress()
    # Simulate creating some records for seeded behaviour (not calling external APIs here)
    # Create 3 sample records
    sample = [
        {'id_from_service': 'svc-1', 'first_name': 'Alice', 'last_name': 'Wang', 'email': 'alice@example.com'},
        {'id_from_service': 'svc-2', 'first_name': 'Bob', 'last_name': 'Li', 'email': 'bob@example.com'},
        {'id_from_service': 'svc-3', 'first_name': 'Carol', 'last_name': 'Zhang', 'email': 'carol@example.com'},
    ]
    for rec in sample:
        ExtractedRecord.objects.create(job=job, **rec, raw=rec)
    job.mark_completed(record_count=len(sample))
    return Response({'job_id': str(job.job_id)}, status=http_status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def scan_status(request, job_id):
    try:
        job = ExtractionJob.objects.get(job_id=job_id)
    except ExtractionJob.DoesNotExist:
        return Response({'detail': 'Job not found'}, status=http_status.HTTP_404_NOT_FOUND)
    serializer = ExtractionJobSerializer(job)
    return Response(serializer.data)


@api_view(['GET'])
def scan_result(request, job_id):
    try:
        job = ExtractionJob.objects.get(job_id=job_id)
    except ExtractionJob.DoesNotExist:
        return Response({'detail': 'Job not found'}, status=http_status.HTTP_404_NOT_FOUND)
    if job.status != ExtractionJob.STATUS_COMPLETED:
        return Response({'detail': 'Job not completed yet'}, status=http_status.HTTP_409_CONFLICT)
    # Support pagination params: limit & offset
    limit = int(request.query_params.get('limit', 100))
    offset = int(request.query_params.get('offset', 0))
    records_qs = job.records.all().order_by('id')
    total = records_qs.count()
    records = records_qs[offset:offset+limit]
    serializer = ExtractedRecordSerializer(records, many=True)
    return Response({'total': total, 'count': len(serializer.data), 'results': serializer.data})


@api_view(['POST'])
def scan_cancel(request, job_id):
    try:
        job = ExtractionJob.objects.get(job_id=job_id)
    except ExtractionJob.DoesNotExist:
        return Response({'detail': 'Job not found'}, status=http_status.HTTP_404_NOT_FOUND)
    if job.status in [ExtractionJob.STATUS_COMPLETED, ExtractionJob.STATUS_FAILED]:
        return Response({'detail': 'Cannot cancel job in current state'}, status=http_status.HTTP_400_BAD_REQUEST)
    job.mark_cancelled()
    return Response({'detail': 'Job cancelled'})


@api_view(['DELETE'])
def scan_remove(request, job_id):
    try:
        job = ExtractionJob.objects.get(job_id=job_id)
    except ExtractionJob.DoesNotExist:
        return Response(status=http_status.HTTP_204_NO_CONTENT)
    job.delete()
    return Response(status=http_status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def jobs_list(request):
    qs = ExtractionJob.objects.all().order_by('-created_at')
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 50))
    start = (page-1) * page_size
    end = start + page_size
    total = qs.count()
    serializer = ExtractionJobSerializer(qs[start:end], many=True)
    return Response({'total': total, 'page': page, 'page_size': page_size, 'results': serializer.data})


@api_view(['GET'])
def jobs_statistics(request):
    total = ExtractionJob.objects.count()
    completed = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_COMPLETED).count()
    pending = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_PENDING).count()
    in_progress = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_IN_PROGRESS).count()
    failed = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_FAILED).count()
    cancelled = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_CANCELLED).count()
    avg_time = None
    # compute average extraction duration for completed jobs if any
    completed_jobs = ExtractionJob.objects.filter(status=ExtractionJob.STATUS_COMPLETED, start_time__isnull=False, end_time__isnull=False)
    if completed_jobs.exists():
        total_seconds = sum([(j.end_time - j.start_time).total_seconds() for j in completed_jobs])
        avg_time = total_seconds / completed_jobs.count()
    return Response({'total': total, 'completed': completed, 'pending': pending, 'in_progress': in_progress, 'failed': failed, 'cancelled': cancelled, 'avg_time_seconds': avg_time})
