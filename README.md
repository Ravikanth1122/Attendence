# Face Attendance App (backend + frontend)

## Backend
- Folder: backend
- Run: create venv, pip install -r requirements.txt, then `uvicorn main:app --reload --port 8000`

## Frontend
- Folder: frontend
- Run: `npm install` then `npm run dev` (Vite)
- Make sure VITE_API_BASE or default http://localhost:8000 is correct

## Notes
- This is a minimal working project. For production, secure endpoints, add authentication, and consider using a proper DB like PostgreSQL.
- facenet-pytorch and torch can be large. Install with GPU support if you have CUDA and want faster embeddings.