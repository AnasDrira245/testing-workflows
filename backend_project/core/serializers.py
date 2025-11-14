from rest_framework import serializers
from .models import Employee, Department

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ExtractedRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = ['id', 'id_from_service', 'first_name', 'last_name', 'email', 'raw', 'created_at']


from .models import ExtractionJob, ExtractedRecord


class ExtractionJobSerializer(serializers.ModelSerializer):
    records = ExtractedRecordSerializer(many=True, read_only=True)

    class Meta:
        model = ExtractionJob
        fields = ['job_id', 'status', 'record_count', 'start_time', 'end_time', 'error_message', 'created_at', 'records']


# fix ExtractedRecordSerializer model reference
ExtractedRecordSerializer.Meta.model = ExtractedRecord
