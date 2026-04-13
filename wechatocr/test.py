import wcocr
import os, json

if os.name == 'nt':
    wechat_path = r"..\wechatocr\wechat\4.1.7.59"
    wechatocr_path = r"..\wechatocr\wechatocr\8082\extracted\wxocr.dll"
else:
    wechat_path = "/opt/wechat"
    wechatocr_path = "/opt/wechat/wxocr"

assert os.path.exists(wechat_path), wechat_path
assert os.path.exists(wechatocr_path), wechatocr_path

wcocr.init(os.path.abspath(wechatocr_path), os.path.abspath(wechat_path))
result = wcocr.ocr("test.png")
print(json.dumps(result, ensure_ascii=False, indent=2))
