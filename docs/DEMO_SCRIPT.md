# CampusAI Competition Demo Script

Suggested duration: 4-6 minutes. The goal is to show a complete learning-material workflow, while being precise that the current AI features are local mock services.

## 1. Project Introduction

Suggested narration:

> CampusAI is an AI-assisted learning-material management and review platform for university students. V0.1 focuses on a complete backend workflow: upload course materials, extract text from supported files, generate local mock summaries and review cards, and search across learning content. The mock AI layer is deliberately local and testable; it is designed to be replaced by a real LLM later.

Show the repository README and briefly point out the V0.1 technology stack.

## 2. Open Interactive Documentation

1. Start the service:

   ```bash
   uvicorn backend.main:app --reload
   ```

2. Open `http://127.0.0.1:8000/docs`.
3. Point out the grouped `courses` and `materials` endpoints.

Suggested narration:

> FastAPI exposes an interactive contract for every endpoint, which lets us demonstrate the current backend without a separate frontend page.

## 3. View Courses and Existing Materials

1. Execute `GET /api/courses`.
2. Select one course ID from the response, such as `1`.
3. Execute `GET /api/courses/1/materials`.

Suggested narration:

> Courses and materials are stored locally in JSON. Material writes are persisted, so the data survives service restarts.

## 4. Upload a Text Material

Prepare a short `demo-notes.txt` file containing two or three sentences about a course topic.

1. Open `POST /api/courses/1/materials/upload`.
2. Choose `demo-notes.txt` for the multipart `file` field.
3. Execute the request and record the returned material `id`.
4. Highlight `filename`, `file_path`, `text_preview`, `text_length`, and `extracted: true` in the response.

Suggested narration:

> Text and Markdown files are extracted locally on upload. Other common learning formats can already be stored, while their richer extraction is a future step.

## 5. Generate a Mock AI Summary

1. Set the returned ID in `POST /api/materials/{material_id}/summary`.
2. Execute the endpoint.
3. Highlight `ai_summary`, `summary_method: mock`, and `summary_updated_at`.

Suggested narration:

> The current summary is a transparent local mock rather than a real model call. This keeps the demo reproducible without an API key while preserving the service boundary for future LLM integration.

## 6. Search Materials

1. Open `GET /api/materials/search`.
2. Use a keyword from the uploaded text or the generated summary, for example `mock summary`.
3. Optionally set `course_id=1` to show scoped search.
4. Highlight the result `course_id` and matching material fields.

Suggested narration:

> Search is read-only and can match material metadata, extracted text, or generated summaries. It helps students find a note after the material collection grows.

## 7. Generate Study Cards

1. Set the same material ID in `POST /api/materials/{material_id}/cards`.
2. Execute the endpoint.
3. Show the three returned cards with their question, answer, card type, and timestamp.
4. Re-run the endpoint once and explain that cards are replaced, not appended indefinitely.
5. Execute `GET /api/courses/1/materials` to show that `cards` and generation metadata are persisted.

Suggested narration:

> The card generator currently uses deterministic rules, prioritizing the mock summary, then extracted text, then the original material summary. It demonstrates how a stored learning resource can become a review artifact.

## 8. Close With Value and Next Steps

Suggested narration:

> CampusAI V0.1 demonstrates a full and testable backend loop from uploaded course material to searchable review aids. The next upgrades are real LLM integration, RAG retrieval with a vector database, richer document extraction, and a student-facing frontend.

Optional closing evidence:

```bash
wsl -d Ubuntu --cd /home/qxrrr/projects/campus-ai \
.venv/bin/python -m unittest backend.tests.test_courses_api
```

Mention that the integration suite validates upload, persistence, text extraction, mock summaries, search, and study cards through real HTTP requests.