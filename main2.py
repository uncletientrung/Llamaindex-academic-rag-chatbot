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
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Định dạng dữ liệu nhận từ frontend
class ChatRequest(BaseModel):
    question: str
    group: str = "all"

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
    group = request.group.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng nhập câu hỏi."
        )
    
    try:
        answer = rag_engine.ask(
            question=question,
            group=group,
        )
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

    if not file.filename or Path(file.filename).name != file.filename:
        raise HTTPException(
            status_code=400,
            detail="Tên file không hợp lệ.",
        )
    if Path(file.filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Định dạng file không được hỗ trợ.",
        )

    # Lưu file thật xuống máy
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    rag_engine.add_document(str(file_path))     # Đưa file vào LlamaIndex

    return {
        "message": "Upload thành công",
        "filename": file.filename,
        "group": group
    }

@app.delete("/documents/file")
def delete_file(group: str = Form(...), filename: str = Form(...)): # Xóa file
    if (not group or group in {".", ".."} or "/" in group or "\\" in group or not filename or Path(filename).name != filename):
        raise HTTPException(
            status_code=400,
            detail="Đường dẫn file không hợp lệ."
        )

    group_dir = (DATA_DIR / group).resolve()
    if group_dir.parent != DATA_DIR or not group_dir.is_dir(): # Nếu thư mục nhóm không có thư mục cha
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhóm tài liệu."
        )

    file_path = (group_dir / filename).resolve()
    if file_path.parent != group_dir: # Nếu file không có thư mục cha
        raise HTTPException(
            status_code=400,
            detail="Đường dẫn file không hợp lệ."
        )

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Định dạng file không được hỗ trợ."
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy file."
        )

    try:
        rag_engine.delete_document(str(file_path))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy file."
        )
    except Exception:
        import logging
        logging.exception("Lỗi khi xóa tài liệu khỏi RAG")
        raise HTTPException(
            status_code=500,
            detail="Không thể xóa tài liệu."
        )

    return {
        "message": "Đã xóa file khỏi thư mục và RAG.",
        "filename": filename,
        "group": group
    }


@app.delete("/groups/{name}")
def delete_group(name: str): # Xóa thư mục
    if (not name or name in {".", ".."} or "/" in name or "\\" in name ):
        raise HTTPException(
            status_code=400,
            detail="Tên nhóm không hợp lệ."
        )

    group_dir = (DATA_DIR / name).resolve()
    if group_dir.parent != DATA_DIR or not group_dir.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy nhóm tài liệu."
        )

    try:
        has_files = any(file.is_file() for file in group_dir.rglob("*")) # check bên trong đó có file hay không
        shutil.rmtree(group_dir) # Xóa toàn bộ thư mục nhóm và các file bên trong
        if has_files:
            rag_engine.rebuild_index()  # Xây dựng lại RAG từ tất cả file còn lại
    except Exception:
        import logging
        logging.exception("Lỗi khi xóa nhóm tài liệu")
        raise HTTPException(
            status_code=500,
            detail="Không thể hoàn tất việc xóa nhóm."
        )

    return {
        "message": "Đã xóa nhóm và cập nhật RAG.",
        "name": name
    }