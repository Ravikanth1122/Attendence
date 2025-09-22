import os, uuid, numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Student, Attendance
from face_utils import read_image_bytes_safe, detect_faces_pil, embed_from_pil_list, embedding_to_bytes, bytes_to_embedding, cosine_similarity
from datetime import date
import shutil

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')
STUDENT_PHOTOS = os.path.join(DATA_DIR, 'students')
UPLOADS = os.path.join(DATA_DIR, 'uploads')
os.makedirs(STUDENT_PHOTOS, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

DATABASE_URL = f'sqlite:///{os.path.join(DATA_DIR, "attendance.db")}'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

MATCH_THRESHOLD = 0.62

app = FastAPI(title='Face Attendance API')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/enroll_student')
async def enroll_student(name: str = Form(...), roll: str = Form(None), file: UploadFile = File(...), db = Depends(get_db)):
    content = await file.read()
    img_pil = read_image_bytes_safe(content)
    faces, boxes = detect_faces_pil(img_pil)
    if not faces:
        raise HTTPException(400, 'No face detected in enrollment photo.')
    # choose largest
    areas = [(b[2]-b[0])*(b[3]-b[1]) for b in boxes]
    idx = int(np.argmax(areas))
    face = faces[idx]
    emb = embed_from_pil_list([face])[0]
    emb_bytes = embedding_to_bytes(emb)
    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(STUDENT_PHOTOS, filename)
    face.save(path)
    student = Student(name=name, roll=roll, photo_path=path, embedding=emb_bytes)
    db.add(student); db.commit(); db.refresh(student)
    return {'status':'ok','student_id': student.id, 'name': student.name}

@app.get('/students')
def list_students(db = Depends(get_db)):
    students = db.query(Student).all()
    out = []
    for s in students:
        out.append({'id': s.id, 'name': s.name, 'roll': s.roll, 'photo_path': s.photo_path, 'created_at': s.created_at.isoformat()})
    return out

@app.delete('/students/{student_id}')
def delete_student(student_id: int, db = Depends(get_db)):
    s = db.query(Student).filter(Student.id==student_id).first()
    if not s:
        raise HTTPException(404, 'Student not found')
    try:
        if s.photo_path and os.path.exists(s.photo_path):
            os.remove(s.photo_path)
    except Exception:
        pass
    db.delete(s); db.commit()
    return {'status':'deleted'}

@app.post('/upload_class_photo')
async def upload_class_photo(file: UploadFile = File(...), date_str: str = Form(None), db = Depends(get_db)):
    content = await file.read()
    img_pil = read_image_bytes_safe(content)
    faces, boxes = detect_faces_pil(img_pil)
    upload_name = f"{uuid.uuid4().hex}.jpg"
    upload_path = os.path.join(UPLOADS, upload_name)
    img_pil.save(upload_path)
    if not faces:
        raise HTTPException(400, 'No faces found.')
    students = db.query(Student).all()
    if not students:
        raise HTTPException(400, 'No enrolled students.')
    emb_list = [bytes_to_embedding(s.embedding) for s in students]
    id_list = [s.id for s in students]
    face_embs = embed_from_pil_list(faces)
    attendance_date = date.fromisoformat(date_str) if date_str else date.today()
    results = []
    for idx, fe in enumerate(face_embs):
        best_sim = -1.0; best_sid = None
        for sid, se in zip(id_list, emb_list):
            sim = cosine_similarity(fe, se)
            if sim > best_sim:
                best_sim = sim; best_sid = sid
        if best_sim >= MATCH_THRESHOLD:
            att = db.query(Attendance).filter(Attendance.student_id==best_sid, Attendance.date==attendance_date).first()
            if not att:
                att = Attendance(student_id=best_sid, date=attendance_date, status='present', score=float(best_sim), photo_path=upload_path)
                db.add(att)
            else:
                att.status='present'; att.score=float(best_sim); att.photo_path=upload_path
            db.commit()
            student = db.query(Student).filter(Student.id==best_sid).first()
            results.append({'detected_face_index': idx, 'student_id': best_sid, 'name': student.name, 'score': best_sim, 'status':'present'})
        else:
            results.append({'detected_face_index': idx, 'student_id': None, 'name': None, 'score': best_sim, 'status':'unknown'})
    present_ids = [r['student_id'] for r in results if r['status']=='present']
    for sid in id_list:
        if sid not in present_ids:
            existing = db.query(Attendance).filter(Attendance.student_id==sid, Attendance.date==attendance_date).first()
            if not existing:
                db.add(Attendance(student_id=sid, date=attendance_date, status='absent', score=None, photo_path=upload_path))
    db.commit()
    att_rows = db.query(Attendance).filter(Attendance.date==attendance_date).all()
    summary = [{'student_id': a.student_id, 'name': a.student.name, 'status': a.status, 'score': a.score} for a in att_rows]
    return {'status':'ok', 'date': attendance_date.isoformat(), 'detections': results, 'summary': summary}

@app.get('/attendance_by_date')
def get_attendance(query_date: str = None, db = Depends(get_db)):
    attendance_date = date.fromisoformat(query_date) if query_date else date.today()
    rows = db.query(Attendance).filter(Attendance.date==attendance_date).all()
    out = []
    for r in rows:
        out.append({'student_id': r.student_id, 'name': r.student.name, 'status': r.status, 'score': r.score})
    return {'date': attendance_date.isoformat(), 'attendance': out}