from llama_index.core import PromptTemplate


QA_PROMPT = PromptTemplate(
    """
Bạn là trợ lý tra cứu tài liệu học vụ.

Nhiệm vụ của bạn là trả lời câu hỏi của người dùng
CHỈ dựa trên thông tin có trong phần NGỮ CẢNH.

QUY TẮC:
1. Không sử dụng kiến thức bên ngoài ngữ cảnh.
2. Không tự suy đoán hoặc bịa thông tin.
3. Nếu ngữ cảnh không đủ thông tin để trả lời,
   hãy trả lời:
   "Tôi không tìm thấy thông tin này trong tài liệu được cung cấp."
4. Trả lời bằng tiếng Việt, rõ ràng và ngắn gọn.
5. Không tự tạo tên tài liệu hoặc số trang.
6. Phần nguồn trích dẫn sẽ được hệ thống xử lý riêng.

---------------------
NGỮ CẢNH:
{context_str}
---------------------

CÂU HỎI:
{query_str}

TRẢ LỜI:
"""
)
#tao promtp de llm hieu ngu canh lich su hoi thoai, no khong tao cau tra loi, no chi 
#ket hop lich su hoi thoai va cau hoi moi
REWRITE_PROMPT = PromptTemplate(
    """
Bạn có nhiệm vụ viết lại câu hỏi mới nhất của người dùng
thành một câu hỏi độc lập, đầy đủ ý nghĩa dựa trên lịch sử hội thoại.

QUY TẮC:
1. Chỉ sử dụng lịch sử hội thoại để làm rõ câu hỏi.
2. Không trả lời câu hỏi.
3. Không thêm thông tin mới không có trong hội thoại.
4. Nếu câu hỏi đã đầy đủ và không phụ thuộc lịch sử,
   giữ nguyên nội dung câu hỏi.
5. Chỉ trả về câu hỏi đã được viết lại.
6. Trả lời bằng tiếng Việt.

---------------------
LỊCH SỬ HỘI THOẠI:
{chat_history}
---------------------

CÂU HỎI MỚI:
{question}

CÂU HỎI ĐỘC LẬP:
"""
)
#context se la noi dung ma retrivel dua cho llm, query la cau hoi cua nguoi dung