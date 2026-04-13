#encoding=utf8
import wcocr
import os, json, sys, tempfile, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import traceback

# 以当前脚本所在目录为基准路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if os.name == 'nt':
    wechat_path = os.path.join(SCRIPT_DIR, r"wechat\4.1.7.59")
    wechatocr_path = os.path.join(SCRIPT_DIR, r"wechatocr\8082\extracted\wxocr.dll")
else:
    wechat_path = "/opt/wechat"
    wechatocr_path = "/opt/wechat/wxocr"

wechat_path = os.path.abspath(wechat_path)
wechatocr_path = os.path.abspath(wechatocr_path)

assert os.path.exists(wechat_path), f"wechat_path not found: {wechat_path}"
assert os.path.exists(wechatocr_path), f"wechatocr_path not found: {wechatocr_path}"

wcocr.init(wechatocr_path, wechat_path)
print(f"[wcocr] initialized, wechat={wechat_path}, ocr={wechatocr_path}")


class OCRHandler(BaseHTTPRequestHandler):
    """
    POST /ocr
      JSON body:
        { "image_path": "C:/abs/path/to/image.png" }
      或
        { "image_base64": "<base64 encoded image data>", "ext": ".png" }

      Response (200):
        { "ok": true, "result": { ... } }

      Error (4xx/5xx):
        { "ok": false, "error": "..." }
    """

    def _send_json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path.rstrip("/") != "/ocr":
            self._send_json(404, {"ok": False, "error": f"Not found: {self.path}"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req = json.loads(body.decode("utf-8")) if body else {}
        except Exception as e:
            traceback.print_exc()
            self._send_json(400, {"ok": False, "error": f"Invalid JSON: {e}"})
            return

        tmp_path = None
        try:
            if "image_path" in req:
                image_path = req["image_path"]
                if not os.path.isabs(image_path):
                    image_path = os.path.join(SCRIPT_DIR, image_path)
                if not os.path.exists(image_path):
                    self._send_json(400, {"ok": False, "error": f"File not found: {image_path}"})
                    return
            elif "image_base64" in req:
                ext = req.get("ext", ".png")
                img_data = base64.b64decode(req["image_base64"])
                fd, tmp_path = tempfile.mkstemp(suffix=ext, dir=SCRIPT_DIR)
                with os.fdopen(fd, "wb") as f:
                    f.write(img_data)
                image_path = tmp_path
            else:
                self._send_json(400, {"ok": False, "error": "Missing 'image_path' or 'image_base64' in request"})
                return

            result = wcocr.ocr(image_path)
            self._send_json(200, {"ok": True, "result": result})

        except Exception as e:
            traceback.print_exc()
            self._send_json(500, {"ok": False, "error": str(e)})
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/", "/health"):
            self._send_json(200, {"ok": True, "message": "wcocr service is running"})
        else:
            self._send_json(404, {"ok": False, "error": f"Not found: {self.path}"})

    def log_message(self, format, *args):
        print(f"[wcocr] {self.address_string()} - {format % args}")


def main():
    host = "0.0.0.0"
    port = 5088
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = HTTPServer((host, port), OCRHandler)
    print(f"[wcocr] HTTP server listening on http://{host}:{port}")
    print(f"[wcocr] POST /ocr  =>  {{'image_path': '...'}} or {{'image_base64': '...', 'ext': '.png'}}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[wcocr] shutting down...")
        server.server_close()


if __name__ == "__main__":
    main()
