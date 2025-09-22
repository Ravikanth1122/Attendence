from sqlalchemy import Column, Integer, String, Date, DateTime, Float, LargeBinary, create_engine, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    roll = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    embedding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    photo_path = Column(String, nullable=True)
    student = relationship("Student")
    __table_args__ = (UniqueConstraint("student_id", "date", name="_student_date_uc"),)