from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
from pydantic import BaseModel
import shutil

from test import RAGEngine


app = FastAPI(title="Academic RAG API")
DATA_DIR = Path("data").resolve()
DATA_DIR.mkdir(exist_ok=True)
rag_engine = RAGEngine()
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Cho phép frontend đang chạy bằng Live Server gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", # Địa chỉ frontend
        "http://localhost:5500",
        "http://127.0.0.1:8000", # Địa chỉ backend  
        "http://localhost:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Định dạng dữ liệu nhận từ frontend
class ChatRequest(BaseModel):
    question: str

# Định dạng dữ liệu trả về frontend
class ChatResponse(BaseModel):
    answer: str

class CreateGroupRequest(BaseModel):
    name: str

@app.get("/")
def home():
    return {"message": "Academic RAG API is running"}

@app.get("/documents")
def get_documents(): # Đọc danh sách nhóm từ thư mục data
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    groups = []
    for group_dir in sorted(DATA_DIR.iterdir()):
        if not group_dir.is_dir():
            continue
        files = []
        for file_path in sorted(group_dir.iterdir()):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            files.append({
                "name": file_path.name,
                "extension": file_path.suffix.lower().lstrip("."),
                "size": file_path.stat().st_size,
                "path": str(file_path.relative_to(DATA_DIR))
            })

        groups.append({
            "name": group_dir.name,
            "files": files
        })

    return {"groups": groups}

@app.post("/chat", response_model=ChatResponse) # response_model=ChatResponse: Khai báo cấu trúc phản hồi mong muốn.
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng nhập câu hỏi."
        )
    try:
        answer = rag_engine.ask(question)
        return ChatResponse(answer=answer)

    except Exception:
        import logging         # Ghi chi tiết lỗi ở terminal để dễ debug
        logging.exception("Lỗi khi xử lý câu hỏi")

        raise HTTPException(
            status_code=500,
            detail="Không thể xử lý câu hỏi. Vui lòng thử lại."
        )

@app.post("/groups")
def create_group(request: CreateGroupRequest): # Tạo thư mục
    name = request.name.strip()
    if not name:
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm không được để trống."
        )
    if name in {".", ".."} or "/" in name or "\\" in name: # Chỉ cho phép tên thư mục đơn giản
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm không hợp lệ."
        )

    group_dir = DATA_DIR / name
    if group_dir.exists():
        raise HTTPException(
            status_code=409,
            detail="Nhóm tài liệu đã tồn tại."
        )

    group_dir.mkdir(parents=True, exist_ok=False)
    return {
        "message": "Tạo nhóm thành công.",
        "name": name
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), group: str = Form(...)):
    group_dir = DATA_DIR / group  # Tạo thư mục theo nhóm tài liệu
    group_dir.mkdir(parents=True, exist_ok=True)
    file_path = group_dir / file.filename # Đường dẫn file

    # Lưu file thật xuống máy
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    rag_engine.add_document(str(file_path))     # Đưa file vào LlamaIndex

    return {
        "message": "Upload thành công",
        "filename": file.filename,
        "group": group
    }