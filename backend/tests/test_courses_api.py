import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class CoursesApiPersistenceTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.tmpdir.name) / "courses.json"
        self.upload_dir = Path(self.tmpdir.name) / "uploads"
        self.data_file.write_text(
            json.dumps(
                {
                    "courses": [
                        {
                            "id": 1,
                            "name": "Computer Organization",
                            "semester": "Junior Year",
                            "description": "Course materials and notes.",
                        },
                        {
                            "id": 7,
                            "name": "Data Structures",
                            "semester": "Sophomore Year",
                            "description": "Stacks, queues, trees, and graphs.",
                        },
                    ],
                    "materials": {
                        "1": [
                            {
                                "id": 101,
                                "title": "Cache Memory Notes",
                                "type": "note",
                                "summary": "Cache basics.",
                            }
                        ],
                        "7": [],
                    },
                }
            ),
            encoding="utf-8",
        )
        self.port = self._free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self._start_server()

    def tearDown(self):
        self._stop_server()
        self.tmpdir.cleanup()

    def test_courses_are_loaded_from_json_file(self):
        response = self._request("GET", "/api/courses")

        self.assertEqual(response["count"], 2)
        self.assertEqual(response["courses"][1]["id"], 7)
        self.assertEqual(response["courses"][1]["name"], "Data Structures")

    def test_created_material_is_written_back_and_survives_service_restart(self):
        created = self._request(
            "POST",
            "/api/courses/1/materials",
            {
                "title": "Pipeline Review",
                "type": "slide",
                "summary": "Pipeline stages and hazards.",
            },
        )

        self.assertEqual(created["id"], 102)
        saved_data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["materials"]["1"][-1], created)

        self._restart_server()
        materials = self._request("GET", "/api/courses/1/materials")

        self.assertEqual(materials["count"], 2)
        self.assertEqual(materials["materials"][-1], created)

    def test_upload_txt_file_is_saved_and_listed_after_restart(self):
        created = self._multipart_request(
            "/api/courses/1/materials/upload",
            "lecture-notes.txt",
            b"Cache mapping and replacement policies.",
            "text/plain",
        )

        self.assertEqual(created["id"], 102)
        self.assertEqual(created["filename"], "lecture-notes.txt")
        self.assertEqual(created["type"], "txt")
        self.assertTrue(created["extracted"])
        self.assertEqual(created["text_length"], len("Cache mapping and replacement policies."))
        self.assertEqual(created["text_preview"], "Cache mapping and replacement policies.")
        saved_file = self.upload_dir / "course_1" / "lecture-notes.txt"
        self.assertEqual(saved_file.read_bytes(), b"Cache mapping and replacement policies.")

        saved_data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["materials"]["1"][-1], created)

        self._restart_server()
        materials = self._request("GET", "/api/courses/1/materials")
        self.assertEqual(materials["materials"][-1], created)

    def test_upload_md_file_extracts_text(self):
        content = "# Machine Learning\n\nGradient descent and model evaluation."
        created = self._multipart_request(
            "/api/courses/1/materials/upload",
            "review.md",
            content.encode("utf-8"),
            "text/markdown",
        )

        self.assertTrue(created["extracted"])
        self.assertEqual(created["text_length"], len(content))
        self.assertEqual(created["text_preview"], content)

    def test_upload_pdf_file_succeeds_without_text_extraction(self):
        created = self._multipart_request(
            "/api/courses/1/materials/upload",
            "slides.pdf",
            b"%PDF-1.4 binary placeholder",
            "application/pdf",
        )

        self.assertFalse(created["extracted"])
        self.assertEqual(created["text_preview"], "")
        self.assertEqual(created["text_length"], 0)

        materials = self._request("GET", "/api/courses/1/materials")
        self.assertEqual(materials["materials"][-1]["filename"], "slides.pdf")
        self.assertFalse(materials["materials"][-1]["extracted"])
    def test_txt_material_can_generate_and_persist_mock_summary(self):
        created = self._multipart_request(
            "/api/courses/1/materials/upload",
            "summary-notes.txt",
            b"Cache memory improves average access time through locality and reuse.",
            "text/plain",
        )

        summary = self._request("POST", f"/api/materials/{created['id']}/summary", {})

        self.assertEqual(summary["id"], created["id"])
        self.assertTrue(summary["summary_generated"])
        self.assertEqual(summary["summary_method"], "mock")
        self.assertTrue(summary["ai_summary"].startswith("Mock summary: "))
        self.assertTrue(summary["summary_updated_at"])

        saved_data = json.loads(self.data_file.read_text(encoding="utf-8"))
        saved_material = saved_data["materials"]["1"][-1]
        self.assertEqual(saved_material["ai_summary"], summary["ai_summary"])
        self.assertEqual(saved_material["summary_method"], "mock")

        materials = self._request("GET", "/api/courses/1/materials")
        listed = next(item for item in materials["materials"] if item["id"] == created["id"])
        self.assertEqual(listed["ai_summary"], summary["ai_summary"])
        self.assertTrue(listed["summary_generated"])

    def test_summary_for_unknown_material_returns_not_found(self):
        status, response = self._request_with_error(
            "POST",
            "/api/materials/9999/summary",
            {},
        )

        self.assertEqual(status, 404)
        self.assertEqual(response["detail"], "Material not found")

    def test_summary_without_text_returns_bad_request(self):
        status, response = self._request_with_error(
            "POST",
            "/api/materials/101/summary",
            {},
        )

        self.assertEqual(status, 400)
        self.assertEqual(response["detail"], "Material has no text available for summary")

    def test_repeated_summary_updates_existing_material_without_duplicates(self):
        created = self._multipart_request(
            "/api/courses/1/materials/upload",
            "repeat-summary.txt",
            b"Pipeline stages and hazards.",
            "text/plain",
        )
        first = self._request("POST", f"/api/materials/{created['id']}/summary", {})
        time.sleep(0.002)
        second = self._request("POST", f"/api/materials/{created['id']}/summary", {})

        materials = self._request("GET", "/api/courses/1/materials")
        matching = [item for item in materials["materials"] if item["id"] == created["id"]]
        self.assertEqual(len(matching), 1)
        self.assertEqual(materials["count"], 2)
        self.assertEqual(second["id"], first["id"])
        self.assertNotEqual(second["summary_updated_at"], first["summary_updated_at"])
    def test_upload_rejects_unsupported_file_type(self):
        status, response = self._multipart_request(
            "/api/courses/1/materials/upload",
            "notes.exe",
            b"not a course document",
            "application/octet-stream",
            expect_error=True,
        )

        self.assertEqual(status, 400)
        self.assertEqual(response["detail"], "Unsupported file type")

    def test_upload_returns_not_found_for_unknown_course(self):
        status, response = self._multipart_request(
            "/api/courses/999/materials/upload",
            "notes.txt",
            b"course does not exist",
            "text/plain",
            expect_error=True,
        )

        self.assertEqual(status, 404)
        self.assertEqual(response["detail"], "Course not found")

    def test_upload_without_file_returns_bad_request(self):
        status, response = self._multipart_request(
            "/api/courses/1/materials/upload",
            None,
            b"",
            "text/plain",
            expect_error=True,
        )

        self.assertEqual(status, 400)
        self.assertEqual(response["detail"], "Uploaded file must have a filename")

    def _request(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _request_with_error(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))
    def _multipart_request(
        self,
        path,
        filename,
        content,
        content_type,
        expect_error=False,
    ):
        boundary = "----CampusAITestBoundary"
        parts = []
        if filename is not None:
            parts.extend(
                [
                    f'--{boundary}\r\n'.encode(),
                    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode(),
                    f"Content-Type: {content_type}\r\n\r\n".encode(),
                    content,
                    b"\r\n",
                ]
            )
        parts.append(f"--{boundary}--\r\n".encode())
        request = Request(
            f"{self.base_url}{path}",
            data=b"".join(parts),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result if not expect_error else (response.status, result)
        except HTTPError as error:
            result = json.loads(error.read().decode("utf-8"))
            if not expect_error:
                raise
            return error.code, result

    def _start_server(self):
        env = os.environ.copy()
        env["CAMPUSAI_COURSE_DATA_FILE"] = str(self.data_file)
        env["CAMPUSAI_UPLOAD_DIR"] = str(self.upload_dir)
        self.server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._wait_for_server()

    def _stop_server(self):
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)

    def _restart_server(self):
        self._stop_server()
        self._start_server()

    def _wait_for_server(self):
        last_error = None
        for _ in range(50):
            if self.server.poll() is not None:
                self.fail("API server exited before becoming ready")
            try:
                self._request("GET", "/health")
                return
            except (HTTPError, URLError, TimeoutError) as error:
                last_error = error
                time.sleep(0.1)
        self.fail(f"API server did not become ready: {last_error}")

    @staticmethod
    def _free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]


if __name__ == "__main__":
    unittest.main()