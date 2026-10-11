from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


# 1. Cấu hình LLM
Settings.llm = Ollama(
    model="qwen2.5:3b",
    request_timeout=120.0,
)

# 2. Cấu hình Embedding
Settings.embed_model = HuggingFaceEmbedding(
    model_name="AITeamVN/Vietnamese_Embedding"
)

# 3. Đọc tài liệu PDF
documents = SimpleDirectoryReader(
    input_files=["data/project.pdf"]
).load_data()

# 4. Tạo Vector Index
index = VectorStoreIndex.from_documents(documents)

# 5. Tạo Query Engine một lần khi khởi động
query_engine = index.as_query_engine(
    similarity_top_k=5
)


# 6. Hàm để FastAPI gọi
def answer_question(question: str) -> str:
    question = question.strip()
    if not question:
        return "Vui lòng nhập câu hỏi."
    response = query_engine.query(question)
    return str(response)


# 7. Chỉ chạy terminal khi thực thi trực tiếp test.py
if __name__ == "__main__":
    while True:
        question = input("\nBạn hỏi: ")

        if question.lower() in ["exit", "quit"]:
            break

        print("\nTrả lời:")
        print(answer_question(question))