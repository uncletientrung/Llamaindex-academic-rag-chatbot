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
- **PDF OCR:** PyMuPDF và DeepDoc + VietOCR

Các giá trị cấu hình chunking, retrieval và model nằm trong [constants.py](constants.py). LLM được khởi tạo trong [ingestion.py](ingestion.py) và [responsesynthesizer.py](responsesynthesizer.py).

## Cấu trúc chính

```text
.
├── main.py                  # FastAPI app và các API
├── ragservice.py            # Indexing, retrieval, generation
├── ingestion.py             # Đọc tài liệu, tạo và nạp index
├── pdf_ingestion.py         # OCR, tách cột và giữ metadata PDF
├── requirements-ocr.txt     # Dependency bổ sung cho OCR DeepDoc + VietOCR
├── constants.py             # Model và tham số RAG
├── postprocessors.py        # Similarity filter và reranker
├── responsesynthesizer.py   # Sinh câu trả lời bằng LlamaIndex
├── chathistory.py           # Lưu lịch sử chat
├── data/                    # Tài liệu, chia theo thư mục nhóm
├── storage/                 # Index đã persist và lịch sử chat
├── frontend/                # Giao diện web tĩnh
└── evaluation/              # Dataset, script và kết quả đánh giá
```

## Công cụ cần thiết

- Python 3.10 trở lên
- LlamaIndex
- DeepDoc + VietOCR (chỉ cần khi xử lý PDF scan; xem phần cài đặt bên dưới)
- [Ollama](https://ollama.com/) để chạy LLM cục bộ; mặc định dùng model `qwen2.5:3b`
- Embedding model `AITeamVN/Vietnamese_Embedding` (được tải từ Hugging Face khi chạy lần đầu)
- Vector store của LlamaIndex (`SimpleVectorStore`), lưu index cục bộ trong `storage/`
- FastAPI và Uvicorn cho backend; giao diện hiện tại dùng HTML, CSS và JavaScript
- Git để clone/mã nguồn; GitHub chỉ cần nếu muốn lưu trữ hoặc chia sẻ repository

> Streamlit có trong `requirements.txt` nhưng ứng dụng hiện tại không dùng Streamlit; giao diện web kết nối tới backend FastAPI.

## Cài đặt

Các bước dưới đây dành cho máy Windows mới. Cài [Git](https://git-scm.com/download/win), [Python 3.10 trở lên](https://www.python.org/downloads/) và [Ollama](https://ollama.com/download) trước. Mở PowerShell tại thư mục muốn đặt project rồi clone:

```powershell
git clone https://github.com/uncletientrung/Llamaindex-academic-rag-chatbot.git
Set-Location .\Llamaindex-academic-rag-chatbot
```

Tạo môi trường Python riêng và cài dependency của project:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu PowerShell chặn kích hoạt môi trường ảo, có thể chạy lệnh này trong cửa sổ hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Cài DeepDoc + VietOCR cho PDF scan

DeepDoc cần PyTorch và các dependency bổ sung. Cài PyTorch CPU trước, sau đó cài danh sách dependency OCR:

```powershell
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-ocr.txt
```

Clone phiên bản DeepDoc đã thử nghiệm vào thư mục `third_party` (đã được Git bỏ qua) và cấu hình đường dẫn model:

```powershell
$deepdocPath = Join-Path $PWD "third_party\deepdoc_vietocr"
New-Item -ItemType Directory -Force (Split-Path $deepdocPath) | Out-Null
git clone https://github.com/hoaivannguyen/deepdoc_vietocr.git $deepdocPath
git -C $deepdocPath checkout 8f7906fd4e78cd0324532298e9062b031b4a320c
[Environment]::SetEnvironmentVariable("DEEPDOC_VIETOCR_PATH", $deepdocPath, "User")
$env:DEEPDOC_VIETOCR_PATH = $deepdocPath
```

`DEEPDOC_VIETOCR_PATH` phải trỏ tới thư mục gốc có `module/`, `onnx/` và `vietocr/weight/`. Lệnh trên lưu biến cho các terminal PowerShell mới và đặt biến cho cửa sổ hiện tại. Nếu chuyển project sang thư mục khác, hãy cập nhật biến này. Mã nguồn DeepDoc và model không nằm trong project Git; mỗi máy cần tự clone và tải chúng.

PDF có text layer hữu ích được trích xuất trực tiếp; PDF scan dùng DeepDoc + VietOCR. PDF có nhiều cột được sắp xếp theo thứ tự đọc. Văn bản trích xuất được lưu để kiểm tra trong `data/<tên nhóm>__<tên file>.txt`.

Tải model LLM mà ứng dụng sử dụng:

```powershell
ollama pull qwen2.5:3b
```

Embedding và reranker được tải từ Hugging Face khi cần; lần chạy đầu tiên có thể mất thêm thời gian và cần kết nối Internet. Trước khi phân phối project hoặc model DeepDoc, hãy kiểm tra điều khoản giấy phép của repository và model.

## Chạy ứng dụng

Mỗi lần chạy trên terminal mới, mở PowerShell tại thư mục project, kích hoạt môi trường ảo và nạp lại đường dẫn DeepDoc đã lưu:

```powershell
.\.venv\Scripts\Activate.ps1
$env:DEEPDOC_VIETOCR_PATH = [Environment]::GetEnvironmentVariable("DEEPDOC_VIETOCR_PATH", "User")
```

Khởi động backend:

```powershell
uvicorn main:app --reload
```

Backend mặc định chạy tại `http://127.0.0.1:8000`. Có thể mở `http://127.0.0.1:8000/docs` để xem và thử các API.

Khi khởi động lần đầu, hãy tạo nhóm và chép tài liệu vào `data/<tên nhóm>/` hoặc tải lên bằng giao diện. Ứng dụng sẽ tạo index; quá trình này có thể mất thời gian do OCR scan và tải embedding/reranker.

### Khởi động giao diện

Giữ backend đang chạy. Mở thư mục `frontend/` bằng tiện ích **Live Server** trong VS Code, sau đó truy cập địa chỉ Live Server, thường là `http://127.0.0.1:5500`.

Không mở `index.html` trực tiếp bằng `file://`, vì trình duyệt có thể chặn các yêu cầu tới API.

## Sử dụng

1. Đảm bảo Ollama và backend đang chạy; mở giao diện bằng Live Server.
2. Vào **Quản lý tài liệu** để tạo nhóm và tải lên PDF, DOCX hoặc TXT. Có thể thêm tài liệu vào thư mục `data/<tên nhóm>/` trước khi khởi động backend.
3. Chọn một nhóm cụ thể hoặc **Tất cả tài liệu** làm phạm vi tìm kiếm.
4. Nhập câu hỏi ở trang **Hỏi đáp RAG**. Câu trả lời được truyền về theo luồng.
5. Các cuộc trò chuyện được lưu trong `storage/chat_store.json`; thời gian tạo được lưu trong `storage/chat_store_metadata.json` và hiển thị dưới tiêu đề trong lịch sử chat.

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
