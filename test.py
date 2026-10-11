from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class RAGEngine:
    def __init__(self):
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

        # Index ban đầu chưa có dữ liệu
        self.index = None

        # Query Engine
        self.query_engine = None

    # =========================
    # 3. Thêm tài liệu
    # =========================
    def add_document(self, file_path: str):

        documents = SimpleDirectoryReader(
            input_files=[file_path]
        ).load_data()

        # Nếu chưa có index
        if self.index is None:

            self.index = VectorStoreIndex.from_documents(
                documents
            )

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