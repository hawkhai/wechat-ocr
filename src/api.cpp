#include "stdafx.h"
#include "wechatocr.h"
#include <google/protobuf/stubs/common.h>

static string json_encode(const string& input) {
	string output;
	output.reserve(input.size() + 2);
	for (auto c : input) {
		switch (c) {
		case '"': output += "\\\"";	break;
		case '\\': output += "\\\\"; break;
		case '\n': output += "\\n"; break;
		case '\r': output += "\\r";	break;
		case '\t': output += "\\t";	break;
		default:
			if (c>=0 && c < 0x20) {
				char buf[16];
				snprintf(buf, sizeof(buf), "\\u%04x", c);
				output += buf;
			} else {
				output.push_back(c);
			}
		}
	}
	return output;
}

static std::unique_ptr<CWeChatOCR> g_instance;

extern "C" EXPORTED_API
bool wechat_ocr(LPCTSTR ocr_exe, LPCTSTR wechat_dir, const char * imgfn, void(*set_res)(const char * dt))
{
	if (!g_instance) {
		if (!ocr_exe || !wechat_dir || !*ocr_exe || !*wechat_dir)
			return false;
		auto ocr = std::make_unique<CWeChatOCR>(ocr_exe, wechat_dir);
		if (!ocr->wait_connection(5000)) {
			return false;
		}
		g_instance = std::move(ocr);
	}

	string json;
	if (!imgfn || !*imgfn) {
		json = "{\"errcode\":0}";
	} else {
		CWeChatOCR::result_t res;
		if (!g_instance->doOCR(imgfn, &res))
			return false;
		json += "{";
		json += "\"errcode\":" + std::to_string(res.errcode) + ",";
		json += "\"imgpath\":\"" + json_encode(res.imgpath) + "\",";
		json += "\"width\":" + std::to_string(res.width) + ",";
		json += "\"height\":" + std::to_string(res.height) + ",";
		auto json_box4 = [](const CWeChatOCR::box4_t& b) -> string {
			char buf[256];
			snprintf(buf, sizeof(buf),
				"[[%.1f,%.1f],[%.1f,%.1f],[%.1f,%.1f],[%.1f,%.1f]]",
				b.x1, b.y1, b.x2, b.y2, b.x3, b.y3, b.x4, b.y4);
			return buf;
		};
		json += "\"ocr_response\":[";
		for (auto& blk : res.ocr_response) {
			json += "{";
			json += "\"left\":" + std::to_string(blk.left) + ",";
			json += "\"top\":" + std::to_string(blk.top) + ",";
			json += "\"right\":" + std::to_string(blk.right) + ",";
			json += "\"bottom\":" + std::to_string(blk.bottom) + ",";
			json += "\"rate\":" + std::to_string(blk.rate) + ",";
			json += "\"text\":\"" + json_encode(blk.text) + "\"";
			if (blk.has_bold)
				json += ",\"bold\":" + string(blk.bold ? "true" : "false");
			if (blk.has_line_box)
				json += ",\"line_box\":" + json_box4(blk.line_box);
			if (blk.has_text_block_origin)
				json += ",\"text_block_origin\":" + json_box4(blk.text_block_origin);
			if (!blk.details.empty()) {
				json += ",\"details\":[";
				for (auto& ch : blk.details) {
					json += "{";
					json += "\"chars\":\"" + json_encode(ch.chars) + "\",";
					json += "\"left\":" + std::to_string(ch.left) + ",";
					json += "\"top\":" + std::to_string(ch.top) + ",";
					json += "\"right\":" + std::to_string(ch.right) + ",";
					json += "\"bottom\":" + std::to_string(ch.bottom) + "";
					json += "},";
				}
				if (json.back() == ',') {
					json.pop_back();
				}
				json += "]";
			}
			json += "},";
		}
		if (json.back() == ',') {
			json.pop_back();
		}
		json += "]";
		if (!res.cpu_report.empty())
			json += ",\"cpu_report\":\"" + json_encode(res.cpu_report) + "\"";
		if (res.time_used > 0)
			json += ",\"time_used\":" + std::to_string(res.time_used);
		json += "}";
	}
	if (set_res) {
		set_res(json.c_str());
	}
	return true;
}

extern "C" EXPORTED_API
void stop_ocr() {
	g_instance.reset();
}
