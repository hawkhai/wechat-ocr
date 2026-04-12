#pragma once
#include "mojocall.h"

class EXPORTED_API CWeChatOCR : protected CMojoCall
{
public:
	struct box4_t {
		float x1, y1, x2, y2, x3, y3, x4, y4; // topleft, topright, bottomright, bottomleft
	};
	struct simple_t {
		string chars;
		float left, top, right, bottom;
	};
	struct text_block_t {
		float left, top, right, bottom;
		float rate;
		string text;
		std::vector<simple_t> details;
		bool has_bold;
		bool bold;
		bool has_line_box;
		box4_t line_box;
		bool has_text_block_origin;
		box4_t text_block_origin;
	};
	struct result_t {
		string imgpath;
		int errcode;
		int width, height;
		std::vector<text_block_t> ocr_response;
		string cpu_report;
		uint64_t time_used = 0;
	};
	static constexpr int STATE_INITED = 2; // extend state vars from base class.
protected:
	int m_version = 300; // wechat version 3.x
	std::mutex m_mutex;
	std::condition_variable m_cv_idpath;
	std::map<uint64_t, std::pair<string, result_t*>> m_idpath;

public:
	CWeChatOCR(LPCTSTR exe, LPCTSTR wcdir);
	~CWeChatOCR() = default;

	int state() const { return m_state; }
	bool wait_connection(int timeout) override;
	bool wait_done(int timeout); //wait for all pending ocr done.
	bool doOCR(crefstr imgpath, result_t* res = nullptr);

protected:
	virtual void OnOCRResult(result_t& ocr_response);
	void ReadOnPush(uint32_t request_id, std::span<std::byte> request_info) override;
};
