from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


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
    model_name="BAAI/bge-m3"
)


# =========================
# 3. Đọc PDF
# =========================

documents = SimpleDirectoryReader(
    input_files=["quyet_dinh.pdf"]
).load_data()


# =========================
# 4. Tạo Vector Index
# =========================

index = VectorStoreIndex.from_documents(documents)


# =========================
# 5. Tạo Query Engine
# =========================

query_engine = index.as_query_engine(
    similarity_top_k=3
)


# =========================
# 6. Hỏi đáp
# =========================

while True:

    question = input("\nBạn hỏi: ")

    if question.lower() in ["exit", "quit"]:
        break

    response = query_engine.query(question)

    print("\nTrả lời:")
    print(response)
