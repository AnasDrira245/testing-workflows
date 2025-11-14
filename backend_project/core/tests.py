from django.test import TestCase
from rest_framework.test import APIClient
from .models import ExtractionJob, ExtractedRecord
import uuid


class ExtractionAPITests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_health(self):
		r = self.client.get('/api/v1/health')
		self.assertEqual(r.status_code, 200)
		self.assertEqual(r.json().get('status'), 'ok')

	def test_start_without_token(self):
		r = self.client.post('/api/v1/scan/start', {})
		self.assertEqual(r.status_code, 400)

	def test_seeded_start_and_results(self):
		# start with token
		r = self.client.post('/api/v1/scan/start', {'api_token': 'token-123'}, format='json')
		self.assertEqual(r.status_code, 202)
		job_id = r.json().get('job_id')
		# status
		r2 = self.client.get(f'/api/v1/scan/status/{job_id}')
		self.assertEqual(r2.status_code, 200)
		self.assertEqual(r2.json().get('status'), 'completed')
		# results
		r3 = self.client.get(f'/api/v1/scan/result/{job_id}')
		self.assertEqual(r3.status_code, 200)
		self.assertEqual(r3.json().get('total'), 3)

	def test_nonexistent_job(self):
		fake = uuid.uuid4()
		r = self.client.get(f'/api/v1/scan/status/{fake}')
		self.assertEqual(r.status_code, 404)

	def test_result_before_completion(self):
		# create job manually
		job = ExtractionJob.objects.create(api_token='t2')
		# ensure status is pending
		r = self.client.get(f'/api/v1/scan/result/{job.job_id}')
		self.assertEqual(r.status_code, 409)

	def test_cancel_completed(self):
		r = self.client.post('/api/v1/scan/start', {'api_token': 'token-xyz'}, format='json')
		job_id = r.json().get('job_id')
		# cancel should fail because job is completed
		r2 = self.client.post(f'/api/v1/scan/cancel/{job_id}')
		self.assertEqual(r2.status_code, 400)

# Create your tests here.
