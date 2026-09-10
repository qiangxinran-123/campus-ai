# CampusAI

CampusAI V0.1 is an AI-assisted learning-material management and review platform for university students. It focuses on a small, demonstrable backend loop: organize course materials, upload learning files, extract text from supported files, generate local mock summaries and review cards, and search across material content.

> Current implementation note: the AI summary and study-card features are deterministic local mock services. CampusAI V0.1 does not call an external LLM API and does not claim real LLM integration.

## Current Status

- Version: `V0.1`
- Current progress: approximately `94%`
- Backend: FastAPI
- Storage: local JSON file
- Verification: `unittest` integration tests that start the API and exercise real HTTP requests

## Technology Stack

- Python 3
- FastAPI and Uvicorn
- Pydantic
- `python-multipart` for file upload
- Local JSON persistence
- Standard-library `unittest`

## Core Features

- Course listing and course-detail APIs
- Course material listing and JSON material creation
- File upload for `.pdf`, `.ppt`, `.pptx`, `.doc`, `.docx`, `.txt`, and `.md`
- Local file storage under `backend/app/uploads/course_{course_id}/`
- Text extraction for `.txt` and `.md`
- Mock AI summary generation with persisted results
- Keyword search across material metadata, extracted text, and mock summaries
- Mock study-card generation with persisted review cards
- JSON write-back that survives service restarts

## API Overview

| Area | Representative API | Purpose |
| --- | --- | --- |
| Health | `GET /health` | Check API availability |
| Courses | `GET /api/courses` | List courses |
| Materials | `GET /api/courses/{course_id}/materials` | List materials for a course |
| Upload | `POST /api/courses/{course_id}/materials/upload` | Upload a course material |
| Summary | `POST /api/materials/{material_id}/summary` | Generate a local mock summary |
| Search | `GET /api/materials/search?q={keyword}&course_id={optional}` | Search materials without changing data |
| Cards | `POST /api/materials/{material_id}/cards` | Generate local mock review cards |

See [API overview](docs/API_OVERVIEW.md) for the full endpoint list and response behavior.

## Project Structure

```text
campus-ai/
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── app/
│   │   ├── api/                    # Course and material routes
│   │   ├── schemas/                # Pydantic request and response models
│   │   ├── services/               # Persistence, extraction, summary, and card services
│   │   ├── data/courses.json       # Default local course and material data
│   │   └── uploads/                # Uploaded material files at runtime
│   └── tests/test_courses_api.py   # HTTP integration tests
├── docs/
│   ├── API_OVERVIEW.md
│   ├── DEMO_SCRIPT.md
│   └── DEVELOPMENT_LOG.md
└── requirements.txt
```

## Local Run

From the project root in WSL or a Linux shell:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

The default data file is `backend/app/data/courses.json`. The following environment variables keep tests and local experiments isolated:

```bash
CAMPUSAI_COURSE_DATA_FILE=/path/to/courses.json
CAMPUSAI_UPLOAD_DIR=/path/to/uploads
```

## Run Tests

```bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai \
.venv/bin/python -m unittest backend.tests.test_courses_api
```

The suite covers course/material APIs, JSON persistence, file upload, text extraction, mock summary generation, search, and study-card generation.

## Mock AI Capabilities

CampusAI V0.1 uses local rule-based services so that the project can be demonstrated without API keys, network access, or cost:

- Mock summaries prefer extracted text and produce a short fixed-prefix summary.
- Mock cards prefer `ai_summary`, then `text_preview`, then the material `summary`.
- Repeated summary or card requests update the existing material record instead of creating duplicate materials.

These services are isolated under `backend/app/services/`, leaving a clear replacement point for a future LLM provider.

## Competition Highlights

- A complete backend workflow rather than isolated API prototypes
- Persistent JSON data across service restarts
- Clear service-layer separation for upload, extraction, summary, search, and cards
- Testable behavior without external AI credentials
- A realistic evolution path from local mock AI to LLM and RAG capabilities

## Roadmap

- Integrate a real LLM provider through the existing service boundary
- Add RAG retrieval with embeddings and a vector database
- Support text extraction for PDF, PowerPoint, and Word files
- Build a student-facing web frontend
- Add authentication, ownership, and course collaboration features
- Add asynchronous processing and richer evaluation metrics

## Supporting Documents

- [Development log](docs/DEVELOPMENT_LOG.md)
- [API overview](docs/API_OVERVIEW.md)
- [Competition demo script](docs/DEMO_SCRIPT.md)