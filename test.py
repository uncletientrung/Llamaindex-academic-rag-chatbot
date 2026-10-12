from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pathlib import Path
from pydantic import BaseModel
import shutil


class RAGEngine:
    def __init__(self, data_dir="data"):
        # =========================
        # 1. Cấu hình LLM
        # =========================
        Settings.llm = Ollama(
            model="qwen2.5:3b",
            request_timeout=120.0,
        )

        # =========================
        # 2. Cấu hình Embedding
        # =========================
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="AITeamVN/Vietnamese_Embedding"
        )

        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index = None
        self.query_engine = None
        self.load_existing_documents()

    def load_existing_documents(self): # Nạp dữ liệu ban đầu
        supported_extensions = {".pdf", ".docx", ".txt"}
        files = [
            str(path)
            for path in self.data_dir.rglob("*") # rglob("*") là duyệt đệ quy tất cả các 
            if path.is_file()
            and path.suffix.lower() in supported_extensions
        ]
        if not files:
            return

        documents = SimpleDirectoryReader(input_files=files).load_data()
        if documents:
            self.index = VectorStoreIndex.from_documents(documents)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5
            )

        print("Đã nạp xong tài liệu vào RAG.")

    def rebuild_index(self):
        supported_extensions = {".pdf", ".docx", ".txt"}
        files = [
            str(path)
            for path in self.data_dir.rglob("*")
            if path.is_file()
            and path.suffix.lower() in supported_extensions
        ]
        # Xóa index cũ trước khi tạo index mới
        self.index = None
        self.query_engine = None
        if not files:
            return
        documents = SimpleDirectoryReader(input_files=files).load_data()
        if documents:
            self.index = VectorStoreIndex.from_documents(documents)
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5
            )

        print(f"Đã xây dựng lại RAG từ {len(files)} file.")

    # =========================
    # 3. Thêm tài liệu
    # =========================
    def add_document(self, file_path: str):
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        # Nếu chưa có index
        if self.index is None:
            self.index = VectorStoreIndex.from_documents(documents)
        # Nếu index đã tồn tại
        else:
            for document in documents:
                self.index.insert(document)

        # Tạo lại Query Engine
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5
        )


    # =========================
    # 4. Đặt câu hỏi
    # =========================
    def ask(self, question: str) -> str:
        question = question.strip()
        if not question:
            return "Vui lòng nhập câu hỏi."
        if self.query_engine is None:
            return "Chưa có tài liệu nào được tải lên."
        response = self.query_engine.query(question)
        return str(response)

    def delete_document(self, file_path: str):
        target = Path(file_path).resolve()
        # Chỉ cho phép xóa file bên trong thư mục dữ liệu
        if not target.is_relative_to(self.data_dir):
            raise ValueError("Đường dẫn tài liệu không hợp lệ.")

        if not target.is_file():
            raise FileNotFoundError("Không tìm thấy tài liệu.")
        target.unlink()
        self.rebuild_index()