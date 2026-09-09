from datetime import datetime, timezone
from pathlib import Path

from backend.app.services.text_extraction_service import TEXT_EXTRACTION_EXTENSIONS


SUMMARY_METHOD = "mock"
SUMMARY_MAX_LENGTH = 160


def _material_text(material: dict) -> str:
    text_preview = material.get("text_preview", "")
    if text_preview and text_preview.strip():
        return text_preview

    file_path = material.get("file_path")
    if not file_path:
        return ""

    path = Path(file_path)
    if path.suffix.lower() not in TEXT_EXTRACTION_EXTENSIONS:
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def generate_mock_summary(material: dict) -> dict:
    text = _material_text(material)
    if not text.strip():
        raise ValueError("Material has no text available for summary")

    compact_text = " ".join(text.split())
    summary = f"Mock summary: {compact_text[:SUMMARY_MAX_LENGTH]}"
    return {
        "ai_summary": summary,
        "summary_generated": True,
        "summary_method": SUMMARY_METHOD,
        "summary_updated_at": datetime.now(timezone.utc).isoformat(),
    }