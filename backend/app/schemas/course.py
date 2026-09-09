from pydantic import BaseModel


class Course(BaseModel):
    id: int
    name: str
    semester: str
    description: str


class Material(BaseModel):
    id: int
    title: str
    type: str
    summary: str


class CourseListResponse(BaseModel):
    count: int
    courses: list[Course]


class MaterialListResponse(BaseModel):
    course_id: int
    count: int
    materials: list[Material]