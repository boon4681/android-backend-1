from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import create_access_token
from auth import get_current_user
from auth import hash_password
from auth import verify_password

from database import Base
from database import engine
from database import get_db

from models import Student
from models import User
from schemas import StudentCreate
from schemas import StudentResponse
from schemas import TokenResponse
from schemas import UserCreate


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


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()

    if existing is not None:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User created"
    }


@app.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer"
    }


@app.get("/students", response_model=list[StudentResponse], dependencies=[Depends(get_current_user)])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).order_by(Student.id).all()


@app.get("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(get_current_user)])
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@app.post("/students", response_model=StudentResponse, dependencies=[Depends(get_current_user)])
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


@app.put("/students/{student_id}", response_model=StudentResponse, dependencies=[Depends(get_current_user)])
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


@app.delete("/students/{student_id}", dependencies=[Depends(get_current_user)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted"
    }
