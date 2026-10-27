# Academic RAG Chatbot

Đồ án xây dựng chatbot hỏi đáp trên tài liệu tiếng Việt bằng **LlamaIndex**. Người dùng có thể quản lý tài liệu theo nhóm, đặt câu hỏi trên một nhóm hoặc trên tất cả tài liệu, và xem lại các cuộc trò chuyện.

> Kho dữ liệu mẫu trong `data/` hiện gồm một số văn bản pháp luật. Có thể thay hoặc bổ sung tài liệu theo nhu cầu.

## Chức năng

- Đọc tài liệu PDF, DOCX và TXT theo từng thư mục nhóm.
- Chia văn bản thành các đoạn, tạo embedding và lưu index trên đĩa.
- Tìm kiếm vector, lọc các kết quả theo độ tương đồng và xếp hạng lại bằng reranker.
- Dùng LLM để chọn nhóm tài liệu khi truy vấn trên tất cả nhóm và tạo câu trả lời theo ngữ cảnh đã tìm được.
- Trả lời theo luồng; lưu lịch sử hội thoại cục bộ.
- Giao diện web tĩnh để hỏi đáp và quản lý nhóm/tài liệu.

## Công nghệ và mô hình

- **Backend:** Python, FastAPI, Uvicorn
- **RAG:** LlamaIndex; vector index lưu cục bộ
- **LLM:** Ollama, mặc định dùng `qwen2.5:3b`
- **Embedding:** Hugging Face model `AITeamVN/Vietnamese_Embedding`
- **Reranker:** `kiencnt2205/vietnamese-legal-reranker-bge-base`
- **Frontend:** HTML, CSS và JavaScript thuần

Các giá trị cấu hình chunking, retrieval và model nằm trong [constants.py](constants.py). LLM được khởi tạo trong [ingestion.py](ingestion.py) và [responsesynthesizer.py](responsesynthesizer.py).

## Cấu trúc chính

```text
.
├── main2.py                 # FastAPI app và các API
├── test.py                  # RAGService: indexing, retrieval, generation
├── ingestion.py             # Đọc tài liệu, tạo và nạp index
├── constants.py             # Model và tham số RAG
├── postprocessors.py        # Similarity filter và reranker
├── responsesynthesizer.py   # Sinh câu trả lời bằng LlamaIndex
├── chathistory.py           # Lưu lịch sử chat
├── data/                    # Tài liệu, chia theo thư mục nhóm
├── storage/                 # Index đã persist và lịch sử chat
├── frontend/                # Giao diện web tĩnh
├── src/                     # Các module và thử nghiệm phát triển
└── evaluation/              # Dataset, script và kết quả đánh giá
```

## Công cụ cần thiết

- Python 3.10 trở lên
- LlamaIndex
- [Ollama](https://ollama.com/) để chạy LLM cục bộ; mặc định dùng model `qwen2.5:3b`
- Embedding model `AITeamVN/Vietnamese_Embedding` (được tải từ Hugging Face khi chạy lần đầu)
- Vector store của LlamaIndex (`SimpleVectorStore`), lưu index cục bộ trong `storage/`
- FastAPI và Uvicorn cho backend; giao diện hiện tại dùng HTML, CSS và JavaScript
- Git để clone/mã nguồn; GitHub chỉ cần nếu muốn lưu trữ hoặc chia sẻ repository

> Streamlit có trong `requirements.txt` nhưng ứng dụng hiện tại không dùng Streamlit; giao diện web kết nối tới backend FastAPI.

## Cài đặt

Mở PowerShell tại thư mục dự án:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Nếu PowerShell chặn kích hoạt môi trường ảo, có thể chạy lệnh này trong cửa sổ hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Tải model LLM mà ứng dụng sử dụng:

```powershell
ollama pull qwen2.5:3b
```

Embedding và reranker được tải từ Hugging Face khi cần; lần chạy đầu tiên có thể mất thêm thời gian và cần kết nối Internet.

## Chạy ứng dụng

### 1. Khởi động backend

Tại thư mục gốc dự án, sau khi kích hoạt môi trường ảo:

```powershell
uvicorn main2:app --reload
```

Backend mặc định chạy tại `http://127.0.0.1:8000`. Có thể mở `http://127.0.0.1:8000/docs` để xem và thử các API.

Khi khởi động, ứng dụng nạp index có sẵn trong `storage/`; nếu chưa có index cho một nhóm tài liệu, ứng dụng sẽ tạo index từ dữ liệu tương ứng trong `data/`. Quá trình này có thể cần nhiều thời gian ở lần chạy đầu.

### 2. Khởi động giao diện

Giao diện gọi API tại `http://127.0.0.1:8000` và backend hiện cho phép CORS từ cổng `5500`. Có thể mở thư mục `frontend/` bằng tiện ích **Live Server** trong VS Code, sau đó truy cập địa chỉ Live Server, thường là `http://127.0.0.1:5500`.

Không mở `index.html` trực tiếp bằng `file://`, vì trình duyệt có thể chặn các yêu cầu tới API.

## Sử dụng

1. Đảm bảo Ollama và backend đang chạy; mở giao diện bằng Live Server.
2. Vào **Quản lý tài liệu** để tạo nhóm và tải lên PDF, DOCX hoặc TXT. Có thể thêm tài liệu vào thư mục `data/<tên nhóm>/` trước khi khởi động backend.
3. Chọn một nhóm cụ thể hoặc **Tất cả tài liệu** làm phạm vi tìm kiếm.
4. Nhập câu hỏi ở trang **Hỏi đáp RAG**. Câu trả lời được truyền về theo luồng.
5. Các cuộc trò chuyện được lưu trong `storage/chat_store.json`.

Mỗi nhóm có index riêng trong `storage/<tên nhóm>/`. Khi tải lên hoặc xóa tài liệu qua giao diện, backend cập nhật lại index của nhóm đó. Không xóa hoặc chỉnh sửa thủ công nội dung trong `storage/` khi ứng dụng đang chạy.

## API chính

| Phương thức | Đường dẫn | Chức năng |
|---|---|---|
| `GET` | `/` | Kiểm tra backend |
| `GET` | `/documents` | Liệt kê nhóm và tài liệu |
| `POST` | `/groups` | Tạo nhóm tài liệu |
| `DELETE` | `/groups/{name}` | Xóa nhóm và cập nhật index |
| `POST` | `/upload` | Tải tài liệu lên và index nhóm |
| `DELETE` | `/documents/file` | Xóa tài liệu và cập nhật index |
| `POST` | `/chat` | Hỏi đáp dạng streaming |
| `GET` | `/conversations` | Liệt kê cuộc trò chuyện |
| `GET` | `/conversations/{conversation_id}` | Lấy tin nhắn của cuộc trò chuyện |
| `DELETE` | `/conversations/{conversation_id}` | Xóa cuộc trò chuyện |

## Đánh giá và kiểm thử

Các script và bộ dữ liệu đánh giá retrieval, response nằm trong `evaluation/`. Một số kiểm thử nằm trong `tests/` và các module `src/`. Có thể chạy bộ kiểm thử bằng:

```powershell
python -m pytest
```

Nếu chưa cài pytest trong môi trường hiện tại, cài bằng `python -m pip install pytest`.

## Lưu ý

- LLM cần Ollama đang chạy và model `qwen2.5:3b` có sẵn cục bộ.
- Embedding model và reranker có thể cần tải về ở lần chạy đầu.
- Dữ liệu, index và lịch sử chat được lưu cục bộ trong `data/` và `storage/`; hãy sao lưu nếu cần giữ lại.
- Đây là đồ án thử nghiệm, không thay thế việc kiểm tra văn bản gốc hoặc tư vấn chuyên môn.
