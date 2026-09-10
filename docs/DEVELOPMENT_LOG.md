# CampusAI Development Log

This log records the incremental development of CampusAI V0.1. Each stage was kept small enough to validate with working APIs and tests before moving to the next capability.

| Stage | Goal | Completed Work | Acceptance | Project Value |
| --- | --- | --- | --- | --- |
| 1 | FastAPI minimum backend | Created the FastAPI application entry point and a simple greeting endpoint. | Service can start and answer a basic request. | Established an executable backend baseline. |
| 2 | Backend foundation | Added application configuration, router aggregation, health check, and project-status endpoints. | Health endpoint confirms service availability. | Created a maintainable application skeleton. |
| 3 | Mock course/material APIs | Added in-memory-style course and material listing routes backed by sample data. | Course and material lists can be requested over HTTP. | Proved the primary learning-material domain flow. |
| 4 | Pydantic models | Introduced typed course and material request/response schemas. | FastAPI validates and documents API payloads. | Improved API consistency and future maintainability. |
| 5 | Material creation | Added the course material creation endpoint. | A material can be created for an existing course; missing courses return 404. | Completed the first material-management write flow. |
| 6/7 | JSON read and persistence | Moved course/material data to `courses.json` and added atomic JSON write-back. | New materials remain available after service restart. | Replaced temporary state with a lightweight persistent store. |
| 8 | File upload | Added multipart upload for common course-material formats and local upload storage. | Uploaded files and material metadata are persisted. | Connected real learning files to the material domain. |
| 9 | Text extraction | Added `.txt` and `.md` extraction with preview, length, and extraction status fields. | Uploaded text files expose extracted metadata after restart. | Prepared materials for downstream AI-assisted workflows. |
| 10 | Mock AI summary | Added a local summary service and `POST /api/materials/{material_id}/summary`. | Summaries persist; no-text and unknown-material cases are handled. | Demonstrated an AI service boundary without API keys or cost. |
| 11 | Material search | Added keyword search across metadata, extracted text, and mock summaries with course filtering. | Search returns correct matches, empty results, and parameter errors. | Made growing material collections discoverable. |
| 12 | Study-card generation | Added local mock review-card generation and persistent cards per material. | Repeated generation replaces cards instead of appending duplicates. | Turned stored materials into a concrete review aid. |
| 13 | Documentation and demo materials | Added project overview, API reference, development log, and presentation script. | Documentation matches the tested V0.1 API surface. | Makes the project easier to assess, demonstrate, and continue. |
| 14 | Final acceptance and release preparation | Checked repository hygiene, expanded ignore rules, verified documentation, and recorded the release checklist. | Full test suite passes and the release tree contains no tracked runtime artifacts. | Makes V0.1 ready for review, demonstration, and handoff. |

## Verification Practice

The API test suite launches Uvicorn against a temporary JSON data file and temporary upload directory. This keeps tests independent from `backend/app/data/courses.json` while validating HTTP behavior, persistence, and service restart behavior.

```bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai \
.venv/bin/python -m unittest backend.tests.test_courses_api
```

## Version Positioning

CampusAI V0.1 is a backend-oriented prototype. Its local mock summary and card services are intentionally transparent placeholders for future real LLM and RAG integration.
