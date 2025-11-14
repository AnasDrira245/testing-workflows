from django.contrib import admin
from .models import Employee, Department, ExtractionJob, ExtractedRecord


# Register your models here.
admin.site.register(Employee)
admin.site.register(Department)


@admin.register(ExtractionJob)
class ExtractionJobAdmin(admin.ModelAdmin):
	list_display = ('job_id', 'status', 'record_count', 'start_time', 'end_time', 'created_at')
	search_fields = ('job_id', 'status')


@admin.register(ExtractedRecord)
class ExtractedRecordAdmin(admin.ModelAdmin):
	list_display = ('id_from_service', 'email', 'job', 'created_at')
	search_fields = ('id_from_service', 'email')
