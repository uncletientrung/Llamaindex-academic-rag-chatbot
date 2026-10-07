from llama_index.core import SummaryIndex, VectorStoreIndex, TreeIndex, SimpleDirectoryReader, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import RetrieverTool
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from rich.pretty import pprint
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.postprocessor import SimilarityPostprocessor



from src.retrieval.retriever import create_retriever
from src.retrieval.reranker import create_reranker


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

# =========================
# 3. Đọc PDF
# =========================

documents = SimpleDirectoryReader(
    input_files=["data/project.pdf"]
).load_data()
documents2 = SimpleDirectoryReader(
    input_files=["data/quyet_dinh.pdf"]
).load_data()


# =========================
# 4. Tạo Vector Index
# =========================

index = VectorStoreIndex.from_documents(documents)
index2 = VectorStoreIndex.from_documents(documents2)


# # =========================
# #  Xử lý retrieval
# # =========================
# vector_retriever = create_retriever(index)
# bm25_retriever = BM25Retriever.from_defaults(docstore=index.docstore, similarity_top_k=5)


# # =========================
# #  Router (Cái RetrieverTool  sẽ được đổi QueryEngineTool sau khi hoàn tất việc tạo ra các retriever của các quy định khác nhau)
# # =========================

# vector_tool = RetrieverTool.from_defaults(
#     retriever=vector_retriever,
#     description="Dùng để tìm kiếm nội dung quy định dựa trên ngữ nghĩa."
# )

# keyword_tool = RetrieverTool.from_defaults(
#     retriever=bm25_retriever,
#     description="Dùng để tìm kiếm khi câu hỏi chứa từ khóa, tên quy định hoặc thuật ngữ cụ thể."
# )

# router_retriever = RouterRetriever(
#     selector=LLMSingleSelector.from_defaults(),
#     retriever_tools=[
#         vector_tool,
#         keyword_tool,
#     ],
# )
# # print("Router Retriever:")
# # pprint(vars(router_retriever))

# # =========================
# #  RouterQueryEngine
# # =========================

query_engine1 = index.as_query_engine(similarity_top_k=5)
query_engine2 = index2.as_query_engine(similarity_top_k=5)

enginetool1 = QueryEngineTool.from_defaults(
    query_engine=query_engine1,
    name="do_an",
    description=(
        "Dùng để trả lời các câu hỏi liên quan đến đồ án, "
        "đề tài đồ án, môn học của đồ án, nội dung đồ án, "
        "mô tả đồ án và các thông tin cụ thể trong tài liệu project.pdf."
    )
)

enginetool2 = QueryEngineTool.from_defaults(
    query_engine=query_engine2,
    name="quy_che_dao_tao",
    description=(
        "Dùng để trả lời các câu hỏi liên quan đến quy chế đào tạo "
        "của Trường Đại học Sài Gòn, bao gồm đăng ký học phần, "
        "rút học phần, điều kiện học tập, học vụ và các quy định đào tạo."
    )
)

query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        enginetool1,
        enginetool2,
    ],
)

# # =========================
# #  Node Postprocessor
# # =========================
# nodes = router_retriever.retrieve("Điều kiện rút học phần là gì?")
# # Metadata Filter

# # SimilarityPostprocessor
# processor = SimilarityPostprocessor(similarity_cutoff=0.1)
# filtered_nodes = processor.postprocess_nodes(nodes)

# # Rerank
# # reranked_nodes = create_reranker(filtered_nodes)

# print("Số node:", len(filtered_nodes))
# pprint(filtered_nodes)


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
