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
        env = os.environ.copy()
        env["CAMPUSAI_COURSE_DATA_FILE"] = str(self.data_file)
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

    def tearDown(self):
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)
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

        self.assertEqual(
            created,
            {
                "id": 102,
                "title": "Pipeline Review",
                "type": "slide",
                "summary": "Pipeline stages and hazards.",
            },
        )
        saved_data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["materials"]["1"][-1], created)

        self._restart_server()
        materials = self._request("GET", "/api/courses/1/materials")

        self.assertEqual(materials["count"], 2)
        self.assertEqual(materials["materials"][-1], created)

    def _request(self, method, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def _restart_server(self):
        self.server.terminate()
        self.server.wait(timeout=5)
        env = os.environ.copy()
        env["CAMPUSAI_COURSE_DATA_FILE"] = str(self.data_file)
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
