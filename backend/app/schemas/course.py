from pydantic import BaseModel


class Course(BaseModel):
    id: int
    name: str
    semester: str
    description: str


class StudyCard(BaseModel):
    id: int
    question: str
    answer: str
    source_material_id: int
    card_type: str
    created_at: str


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
    cards: list[StudyCard] | None = None
    cards_generated: bool | None = None
    cards_generated_at: str | None = None
    cards_method: str | None = None


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


class MaterialSearchResult(Material):
    course_id: int


class MaterialSearchResponse(BaseModel):
    query: str
    course_id: int | None = None
    count: int
    materials: list[MaterialSearchResult]


class CardGenerationResponse(BaseModel):
    material_id: int
    count: int
    cards: list[StudyCard]
    cards_generated: bool
    cards_generated_at: str