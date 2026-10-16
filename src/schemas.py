from pydantic import BaseModel


class StudentBase(BaseModel):
    student_code: str
    name: str
    major: str


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int

    class Config:
        from_attributes = True
