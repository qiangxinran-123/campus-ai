from fastapi import APIRouter, HTTPException

from backend.app.schemas.course import Material
from backend.app.services.course_service import (
    get_material_by_id,
    update_material,
)
from backend.app.services.summary_service import generate_mock_summary

router = APIRouter(prefix="/api/materials", tags=["materials"])


@router.post("/{material_id}/summary", response_model=Material, response_model_exclude_none=True, response_model_exclude_unset=True)
def generate_material_summary(material_id: int):
    material = get_material_by_id(material_id)

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        summary_fields = generate_mock_summary(material)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return update_material(material_id, summary_fields)