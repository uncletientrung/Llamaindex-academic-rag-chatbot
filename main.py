from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.tools import RetrieverTool
from llama_index.core.selectors import LLMSingleSelector
from rich.pretty import pprint
from llama_index.retrievers.bm25 import BM25Retriever



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
#  Xử lý retrieval
# =========================
vector_retriever = create_retriever(index)
bm25_retriever = BM25Retriever.from_defaults(docstore=index.docstore, similarity_top_k=2)


# =========================
#  Router (Cái RetrieverTool  sẽ được đổi QueryEngineTool sau khi hoàn tất việc tạo ra các retriever của các quy định khác nhau)
# =========================

vector_tool = RetrieverTool.from_defaults(
    retriever=vector_retriever,
    description="Dùng để tìm kiếm nội dung quy định dựa trên ngữ nghĩa."
)

keyword_tool = RetrieverTool.from_defaults(
    retriever=bm25_retriever,
    description="Dùng để tìm kiếm khi câu hỏi chứa từ khóa, tên quy định hoặc thuật ngữ cụ thể."
)

router_retriever = RouterRetriever(
    selector=LLMSingleSelector.from_defaults(),
    retriever_tools=[
        vector_tool,
        keyword_tool,
    ],
)
# print("Router Retriever:")
# pprint(vars(router_retriever))

nodes = router_retriever.retrieve("Điều kiện rút học phần là gì?")
print("Số node:", len(nodes))
pprint(nodes)


# =========================
# 6. Hỏi đáp
# =========================

# while True:

#     question = input("\nBạn hỏi: ")

#     if question.lower() in ["exit", "quit"]:
#         break

#     response = query_engine.query(question)

#     print("\nTrả lời:")
#     print(response)