# CampusAI API Overview

Base URL during local development: `http://127.0.0.1:8000`

Interactive Swagger UI: `GET /docs`

## System and Course APIs

| Method | Path | Function | Key Parameters | Success | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| GET | `/` | API welcome information | None | `200` with project metadata | None expected |
| GET | `/hello` | Minimum backend greeting | None | `200` with a greeting | None expected |
| GET | `/health` | Service health check | None | `200` with `status: ok` | None expected |
| GET | `/api/project/status` | Bootstrap project-status metadata | None | `200` with static status metadata | None expected |
| GET | `/api/courses` | List all courses | None | `200` with `count` and `courses` | None expected |
| GET | `/api/courses/{course_id}` | Read a course | `course_id` path parameter | `200` with course data | `404` when the course does not exist |
| GET | `/api/courses/{course_id}/materials` | List a course's materials | `course_id` path parameter | `200` with `count` and `materials` | `404` when the course does not exist |
| POST | `/api/courses/{course_id}/materials` | Create JSON material metadata | `course_id`; JSON `title`, `type`, `summary` | `201` with the new material | `404` when the course does not exist; validation error for invalid body |

## Upload and Text Extraction

| Method | Path | Function | Key Parameters | Success | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/courses/{course_id}/materials/upload` | Upload and register a material file | `course_id`; multipart form field `file` | `201`; file is stored and material metadata is persisted | `400` for no filename or unsupported type; `404` for unknown course |

Supported upload extensions: `.pdf`, `.ppt`, `.pptx`, `.doc`, `.docx`, `.txt`, `.md`.

For `.txt` and `.md`, the response and saved material include `text_preview`, `text_length`, and `extracted: true`. Other currently allowed formats upload successfully with `extracted: false`, an empty preview, and zero text length.

## Mock AI and Review APIs

| Method | Path | Function | Key Parameters | Success | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| POST | `/api/materials/{material_id}/summary` | Generate a local mock summary and persist it | `material_id` path parameter | `200` with updated material fields such as `ai_summary` and `summary_updated_at` | `404` for unknown material; `400` when no usable text is available |
| POST | `/api/materials/{material_id}/cards` | Generate and persist three local mock study cards | `material_id` path parameter | `200` with `material_id`, `count`, `cards`, and `cards_generated_at` | `404` for unknown material; `400` when no usable text is available |

A study card contains:

```json
{
  "id": 10201,
  "question": "What is the core topic of this material?",
  "answer": "Mock summary: ...",
  "source_material_id": 102,
  "card_type": "concept",
  "created_at": "2026-01-01T00:00:00+00:00"
}
```

The summary and card generators are local mock implementations. They do not call an external model provider.

## Search API

| Method | Path | Function | Key Parameters | Success | Failure Behavior |
| --- | --- | --- | --- | --- | --- |
| GET | `/api/materials/search` | Search materials without modifying JSON data | Required `q`; optional `course_id` | `200` with `query`, `count`, and matching materials that include `course_id` | `400` for missing/blank `q`; `404` for unknown `course_id` |

Search is case-insensitive and checks `title`, `summary`, `filename`, `text_preview`, and `ai_summary`.

Example:

```text
GET /api/materials/search?q=cache&course_id=1
```

## Persistence Notes

- Default course and material data: `backend/app/data/courses.json`
- Default file-upload root: `backend/app/uploads/`
- `CAMPUSAI_COURSE_DATA_FILE` overrides the data file for tests or isolated environments.
- `CAMPUSAI_UPLOAD_DIR` overrides the upload directory for tests or isolated environments.