from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.tools import RetrieverTool
from llama_index.core.selectors import LLMSingleSelector
from rich.pretty import pprint
from llama_index.retrievers.bm25 import BM25Retriever
from src.ingestion.Index import create_all_indexes


from src.retrieval.retriever import create_retriever


# =========================
# 1. Cấu hình LLM
# =========================

Settings.llm = Ollama(
    model="qwen2.5:0.5b",
    request_timeout=120.0,
)


# =========================
# 2. Cấu hình Embedding
# =========================

Settings.embed_model = HuggingFaceEmbedding(
    model_name="AITeamVN/Vietnamese_Embedding"
)

# Settings.embed_model = HuggingFaceEmbedding(
#     model_name="dangvantuan/vietnamese-embedding"
# )

if __name__ == "__main__":
    print("Bắt đầu chạy Ingestion với Ollama...")
    try:
        # Hệ thống lúc này sẽ dùng Qwen để xây TreeIndex, KeywordTableIndex...
        indexes = create_all_indexes()
        print("✅ Thành công! Hệ thống chạy mượt mà.")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")