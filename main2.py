from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from test import answer_question


app = FastAPI(title="Academic RAG API")


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

@app.get("/")
def home():
    return {"message": "Academic RAG API is running"}

@app.post("/chat", response_model=ChatResponse) # response_model=ChatResponse: Khai báo cấu trúc phản hồi mong muốn.
def chat(request: ChatRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Vui lòng nhập câu hỏi."
        )
    try:
        answer = answer_question(question)
        return ChatResponse(answer=answer)

    except Exception:
        # Ghi chi tiết lỗi ở terminal để dễ debug
        import logging
        logging.exception("Lỗi khi xử lý câu hỏi")

        raise HTTPException(
            status_code=500,
            detail="Không thể xử lý câu hỏi. Vui lòng thử lại."
        )