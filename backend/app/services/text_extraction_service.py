from pathlib import Path


TEXT_EXTRACTION_EXTENSIONS = {".txt", ".md"}


def extract_text_from_file(file_path: Path) -> dict:
    if file_path.suffix.lower() not in TEXT_EXTRACTION_EXTENSIONS:
        return {
            "text_preview": "",
            "text_length": 0,
            "extracted": False,
        }

    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {
            "text_preview": "",
            "text_length": 0,
            "extracted": False,
        }

    return {
        "text_preview": text[:300],
        "text_length": len(text),
        "extracted": True,
    }