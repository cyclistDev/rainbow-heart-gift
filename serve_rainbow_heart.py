import json
import uuid
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parent
IMAGES_DIR = PROJECT_ROOT / "images"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


class RainbowHeartHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path == "/api/gallery":
            self.send_gallery_images()
            return
        super().do_GET()

    def do_POST(self):
        if urlsplit(self.path).path != "/api/captures":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Invalid content length")
            return

        content_type = self.headers.get_content_type()
        if content_type != "image/jpeg":
            self.send_error(415, "Only JPEG camera captures are accepted")
            return
        if content_length < 4 or content_length > MAX_UPLOAD_BYTES:
            self.send_error(413, "Camera capture must be under 10 MB")
            return

        image_data = self.rfile.read(content_length)
        if len(image_data) != content_length or not image_data.startswith(b"\xff\xd8\xff"):
            self.send_error(400, "Invalid JPEG image")
            return

        filename = "camera_capture_{}_{}.jpg".format(
            datetime.now().strftime("%Y%m%d_%H%M%S"),
            uuid.uuid4().hex[:8],
        )
        destination = IMAGES_DIR / filename
        try:
            with destination.open("xb") as image_file:
                image_file.write(image_data)
        except OSError:
            self.send_error(500, "Could not save the camera capture")
            return

        self.send_json(
            {"src": "/images/{}".format(filename), "caption": "Camera capture"},
            status=201,
        )

    def send_gallery_images(self):
        images = []
        for image_path in sorted(IMAGES_DIR.glob("camera_capture_*.jpg"), reverse=True):
            images.append(
                {
                    "src": "/images/{}".format(image_path.name),
                    "caption": "Camera capture",
                }
            )
        self.send_json({"images": images})

    def send_json(self, payload, status=200):
        response = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RainbowHeartHandler)
    print("Rainbow Heart is available at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop the local server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Rainbow Heart server.")
    finally:
        server.server_close()
.
