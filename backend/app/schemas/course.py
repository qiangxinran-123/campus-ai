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
    filename: str | None = None
    file_path: str | None = None
    text_preview: str = ""
    text_length: int = 0
    extracted: bool = False
    ai_summary: str | None = None
    summary_generated: bool | None = None
    summary_method: str | None = None
    summary_updated_at: str | None = None


class MaterialCreate(BaseModel):
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