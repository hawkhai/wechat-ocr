import wcocr
import os, json

if os.name == 'nt':
    wechat_path = r"D:\Program Files\Tencent\Weixin\4.1.7.59"
    wechatocr_path = os.getenv("APPDATA") + r"\Tencent\xwechat\XPlugin\Plugins\WeChatOcr\8082\extracted\wxocr.dll"
else:
    wechat_path = "/opt/wechat"
    wechatocr_path = "/opt/wechat/wxocr"

wcocr.init(wechatocr_path, wechat_path)
result = wcocr.ocr("test.png")
print(json.dumps(result, ensure_ascii=False, indent=2))
