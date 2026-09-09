from fastapi import APIRouter, HTTPException

from backend.app.schemas.course import (
    Course,
    CourseListResponse,
    Material,
    MaterialCreate,
    MaterialListResponse,
)
from backend.app.services.course_service import (
    create_material,
    get_course,
    list_courses as service_list_courses,
    list_materials,
)

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=CourseListResponse)
def list_courses():
    courses = service_list_courses()

    return {
        "count": len(courses),
        "courses": courses,
    }


@router.get("/{course_id}", response_model=Course)
def get_course_detail(course_id: int):
    course = get_course(course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return course


@router.get("/{course_id}/materials", response_model=MaterialListResponse)
def list_course_materials(course_id: int):
    course = get_course(course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    materials = list_materials(course_id)

    return {
        "course_id": course_id,
        "count": len(materials),
        "materials": materials,
    }


@router.post("/{course_id}/materials", response_model=Material, status_code=201)
def create_course_material(course_id: int, material: MaterialCreate):
    course = get_course(course_id)

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return create_material(course_id, material)