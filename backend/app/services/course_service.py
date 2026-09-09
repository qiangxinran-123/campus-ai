import json
import os
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile


DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "courses.json"
DATA_FILE = Path(os.getenv("CAMPUSAI_COURSE_DATA_FILE", DEFAULT_DATA_FILE))
DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR = Path(os.getenv("CAMPUSAI_UPLOAD_DIR", DEFAULT_UPLOAD_DIR))
SUPPORTED_UPLOAD_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".txt", ".md"}


def load_course_data():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_course_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=DATA_FILE.parent,
        delete=False,
    ) as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
        temp_file = Path(file.name)

    temp_file.replace(DATA_FILE)


def list_courses():
    data = load_course_data()
    return data["courses"]


def get_course(course_id: int):
    courses = list_courses()

    for course in courses:
        if course["id"] == course_id:
            return course

    return None


def list_materials(course_id: int):
    data = load_course_data()
    materials = data["materials"]

    return materials.get(str(course_id), [])


def create_material(course_id: int, material):
    data = load_course_data()
    materials = data["materials"]
    course_materials = materials.setdefault(str(course_id), [])

    next_id = max((item["id"] for item in course_materials), default=course_id * 100) + 1

    new_material = {
        "id": next_id,
        "title": material.title,
        "type": material.type,
        "summary": material.summary,
    }

    course_materials.append(new_material)
    save_course_data(data)

    return new_material


def create_uploaded_material(course_id: int, filename: str, file_object):
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise ValueError("Unsupported file type")

    data = load_course_data()
    course_materials = data["materials"].setdefault(str(course_id), [])
    next_id = max((item["id"] for item in course_materials), default=course_id * 100) + 1

    safe_filename = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    course_upload_dir = UPLOAD_DIR / f"course_{course_id}"
    course_upload_dir.mkdir(parents=True, exist_ok=True)
    destination = course_upload_dir / safe_filename
    with destination.open("wb") as output_file:
        shutil.copyfileobj(file_object, output_file)

    new_material = {
        "id": next_id,
        "title": Path(safe_filename).stem,
        "type": extension[1:],
        "summary": f"Uploaded course material: {safe_filename}",
        "filename": safe_filename,
        "file_path": str(destination),
    }
    course_materials.append(new_material)
    try:
        save_course_data(data)
    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return new_material
