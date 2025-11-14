from django.db import models

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Department(models.Model):
    name = models.CharField(max_length=100)
    employees = models.ManyToManyField(Employee, related_name="departments")

    def __str__(self):
        return self.name


import uuid
from django.utils import timezone


class ExtractionJob(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.BigAutoField(primary_key=True)
    job_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    api_token = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    record_count = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def mark_in_progress(self):
        self.status = self.STATUS_IN_PROGRESS
        self.start_time = timezone.now()
        self.save()

    def mark_completed(self, record_count=0):
        self.status = self.STATUS_COMPLETED
        self.record_count = record_count
        self.end_time = timezone.now()
        self.save()

    def mark_cancelled(self):
        self.status = self.STATUS_CANCELLED
        self.end_time = timezone.now()
        self.save()

    def mark_failed(self, msg=''):
        self.status = self.STATUS_FAILED
        self.error_message = msg
        self.end_time = timezone.now()
        self.save()

    def __str__(self):
        return f"ExtractionJob {self.job_id} ({self.status})"


class ExtractedRecord(models.Model):
    job = models.ForeignKey(ExtractionJob, related_name='records', on_delete=models.CASCADE)
    id_from_service = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    raw = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record {self.id_from_service} for job {self.job.job_id}"
