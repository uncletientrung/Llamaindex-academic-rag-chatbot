TITLE_NODE_PROMT = """
Bạn là trợ lý chuyên phân tích quy chế học vụ đại học tại Sài Gòn.

Hãy đọc đoạn văn bản sau và tạo một tiêu đề ngắn gọn bằng tiếng Việt,
phản ánh chính xác nội dung quy định.

Yêu cầu:
- Chỉ trả về tiêu đề bằng tiếng Việt.
- Không giải thích, không thêm lời dẫn.
- Giữ nguyên số điều, số khoản và thuật ngữ pháp lý nếu cần.
- Không tự suy diễn nội dung không có trong văn bản.

Văn bản:
{context_str}

Tiêu đề tiếng Việt:
"""

TITLE_COMBINE_PROMT = """
Dựa trên các tiêu đề gợi ý và nội dung dưới đây,
hãy tạo một tiêu đề tổng quát bằng tiếng Việt cho tài liệu.

Yêu cầu:
- Ngắn gọn, chính xác, phù hợp với quy định học vụ.
- Không dịch sang tiếng Anh.
- Không bổ sung thông tin không có trong nội dung.

Nội dung:
{context_str}

Tiêu đề tiếng Việt:
"""

KEYWORD_PROMT = """
Bạn là chuyên gia phân tích văn bản quy định học vụ đại học Sài Gòn.

Hãy trích xuất {keywords} từ khóa quan trọng nhất từ văn bản dưới đây.

Yêu cầu:
- Sử dụng tiếng Việt.
- Giữ nguyên số hiệu văn bản, tên riêng và thuật ngữ gốc.
- Không dịch sang tiếng Anh.
- Không giải thích.
- Chỉ trả về các từ khóa, phân cách bằng dấu phẩy.

Văn bản:
{context_str}

Từ khóa:
"""

