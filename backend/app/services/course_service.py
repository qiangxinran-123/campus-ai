import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "courses.json"
DATA_FILE = Path(os.getenv("CAMPUSAI_COURSE_DATA_FILE", DEFAULT_DATA_FILE))


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
