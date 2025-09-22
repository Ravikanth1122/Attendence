# Backend - Face Attendance API

## Run locally
1. Create venv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Start server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
Endpoints:
- POST /enroll_student (form: name, roll, file)
- GET /students
- DELETE /students/{id}
- POST /upload_class_photo (form: file, date_str optional)
- GET /attendance_by_date?query_date=YYYY-MM-DD