"""
测试 wcocr HTTP 服务 (wcocr_serv.py)
请先启动服务: python wcocr_serv.py
"""
import os, json, base64, urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_URL = "http://localhost:5088/ocr"


def ocr_by_path(image_path):
    """通过文件路径调用 OCR"""
    payload = json.dumps({"image_path": image_path}).encode("utf-8")
    req = urllib.request.Request(SERVER_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ocr_by_base64(image_path):
    """读取本地文件，以 base64 方式调用 OCR"""
    ext = os.path.splitext(image_path)[1]
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    payload = json.dumps({"image_base64": img_b64, "ext": ext}).encode("utf-8")
    req = urllib.request.Request(SERVER_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


if __name__ == "__main__":
    test_image = os.path.join(SCRIPT_DIR, "test.png")

    print("=== 方式一: image_path ===")
    result1 = ocr_by_path(test_image)
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    print("\n=== 方式二: image_base64 ===")
    result2 = ocr_by_base64(test_image)
    print(json.dumps(result2, ensure_ascii=False, indent=2))
