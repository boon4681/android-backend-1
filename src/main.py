from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database import Base
from database import engine
from database import get_db

from models import Student
from schemas import StudentCreate
from schemas import StudentResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Management API",
    version="1.0"
)


@app.get("/")
def root():
    return {
        "message": "Student Management API"
    }


@app.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).order_by(Student.id).all()


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(
        student_code=student.student_code,
        name=student.name,
        major=student.major
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.id == student_id).first()

    if existing is None:
        raise HTTPException(status_code=404, detail="Student not found")

    existing.student_code = student.student_code
    existing.name = student.name
    existing.major = student.major

    db.commit()
    db.refresh(existing)

    return existing


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted"
    }
