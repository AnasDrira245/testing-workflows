# Backend Project (GreenTree Data Extraction Service - Sample)

This Django project implements a simple Data Extraction Service API used for testing workflows described in the assignment.

Requirements
- Python 3.11+ (project created against Django 5.x)
- pip

Setup
1. Create a virtualenv and activate it

   python -m venv .venv
   .\.venv\Scripts\activate

2. Install dependencies

   pip install -r requirements.txt

3. Copy `.env.example` to `.env` and fill values

4. Run migrations

   python manage.py migrate

5. Run tests

   python manage.py test

API Endpoints
- Swagger UI: /swagger/
- Health: GET /api/v1/health
- Start scan: POST /api/v1/scan/start {"api_token": "..."}
- Status: GET /api/v1/scan/status/<job_id>
- Results: GET /api/v1/scan/result/<job_id>
- Cancel: POST /api/v1/scan/cancel/<job_id>
- Remove: DELETE /api/v1/scan/remove/<job_id>
- Jobs list: GET /api/v1/jobs/jobs
- Jobs stats: GET /api/v1/jobs/statistics

Notes
- This project uses a simple in-process seeded behavior for `scan/start` that immediately creates sample records. Replace with real extraction logic when integrating with external services.
