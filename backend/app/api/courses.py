from fastapi import APIRouter, HTTPException

from backend.app.schemas.course import (
    Course,
    CourseListResponse,
    Material,
    MaterialCreate,
    MaterialListResponse,
)

router = APIRouter(prefix="/api/courses", tags=["courses"])


COURSES = [
    {
        "id": 1,
        "name": "Computer Organization",
        "semester": "Junior Year",
        "description": "Course materials and notes for computer organization.",
    },
    {
        "id": 2,
        "name": "Machine Learning",
        "semester": "Junior Year",
        "description": "Basic machine learning concepts, assignments, and review notes.",
    },
]


MATERIALS = {
    1: [
        {
            "id": 101,
            "title": "Cache Memory Notes",
            "type": "note",
            "summary": "Key ideas about cache hit, cache miss, and set associative cache.",
        },
        {
            "id": 102,
            "title": "Pipeline Slides",
            "type": "slide",
            "summary": "Introduction to CPU pipeline stages and hazards.",
        },
    ],
    2: [
        {
            "id": 201,
            "title": "Linear Regression Notes",
            "type": "note",
            "summary": "Loss function, gradient descent, and model evaluation.",
        }
    ],
}


@router.get("", response_model=CourseListResponse)
def list_courses():
    return {
        "count": len(COURSES),
        "courses": COURSES,
    }


@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int):
    for course in COURSES:
        if course["id"] == course_id:
            return course

    raise HTTPException(status_code=404, detail="Course not found")


@router.get("/{course_id}/materials", response_model=MaterialListResponse)
def list_course_materials(course_id: int):
    course_exists = any(course["id"] == course_id for course in COURSES)

    if not course_exists:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "course_id": course_id,
        "count": len(MATERIALS.get(course_id, [])),
        "materials": MATERIALS.get(course_id, []),
    }

@router.post("/{course_id}/materials", response_model=Material, status_code=201)
def create_course_material(course_id: int, material: MaterialCreate):
    course_exists = any(course["id"] == course_id for course in COURSES)

    if not course_exists:
        raise HTTPException(status_code=404, detail="Course not found")

    course_materials = MATERIALS.setdefault(course_id, [])
    next_id = max((item["id"] for item in course_materials), default=course_id * 100) + 1

    new_material = {
        "id": next_id,
        "title": material.title,
        "type": material.type,
        "summary": material.summary,
    }

    course_materials.append(new_material)

    return new_material