from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.course import (
    Material,
    MaterialSearchResponse,
)
from backend.app.services.course_service import (
    get_course,
    get_material_by_id,
    search_materials,
    update_material,
)
from backend.app.services.summary_service import generate_mock_summary

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.get("/search", response_model=MaterialSearchResponse)
def search_course_materials(
    q: str | None = Query(default=None),
    course_id: int | None = Query(default=None),
):
    if q is None or not q.strip():
        raise HTTPException(status_code=400, detail="Search keyword must not be empty")
    if course_id is not None and get_course(course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found")

    materials = search_materials(q, course_id)
    return {
        "query": q,
        "course_id": course_id,
        "count": len(materials),
        "materials": materials,
    }


@router.post(
    "/{material_id}/summary",
    response_model=Material,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
)
def generate_material_summary(material_id: int):
    material = get_material_by_id(material_id)

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        summary_fields = generate_mock_summary(material)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return update_material(material_id, summary_fields)