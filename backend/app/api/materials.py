from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.course import (
    CardGenerationResponse,
    Material,
    MaterialSearchResponse,
)
from backend.app.services.card_service import generate_mock_cards
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


@router.post("/{material_id}/cards", response_model=CardGenerationResponse)
def generate_material_cards(material_id: int):
    material = get_material_by_id(material_id)

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        card_fields = generate_mock_cards(material)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    updated_material = update_material(material_id, card_fields)
    return {
        "material_id": updated_material["id"],
        "count": len(updated_material["cards"]),
        "cards": updated_material["cards"],
        "cards_generated": updated_material["cards_generated"],
        "cards_generated_at": updated_material["cards_generated_at"],
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