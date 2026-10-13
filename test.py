from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from pydantic import BaseModel
import shutil
from pipeline import DocumentIngestionPipeline
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from src.promts.promt_qa import  QA_PROMPT
from constants import (
    ALL_GROUPS,
    SUPPORTED_EXTENSIONS,
    SIMILARITY_TOP_K
)
   

class RAGService:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pipeline = DocumentIngestionPipeline(data_dir=self.data_dir)

        self.indices: dict[str, VectorStoreIndex] = {} # dict chứa các index cho từng folder
        self.query_engines = {} # dict chứa các query engine cho từng folder. Dùng cho chế độ chọn mục riêng để hỏi
        self.router_query_engine = None # Cái này dùng cho chế độ chọn tất cả tài liệu

        self.rebuild_index()

    def rebuild_index(self):
        self.indices = self.pipeline.build_indexes()
        self.query_engines = {}
        self.router_query_engine = None

        for group_name, index in self.indices.items(): #  query engine riêng cho mỗi folder
            query_engine = index.as_query_engine(
                text_qa_template = QA_PROMPT,
                similarity_top_k=SIMILARITY_TOP_K,
                streaming=True # Bật streaming
            )
            self.query_engines[group_name] = query_engine

        tools = []  # Tạo các Engine tool
        for group_name, query_engine in self.query_engines.items():
            tool = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                name=f"search_{group_name}",
                description=(
                    f"Tìm kiếm và trả lời câu hỏi dựa trên tài liệu thuộc nhóm {group_name}. "
                    f"Chọn công cụ này khi câu hỏi liên quan đến nội dung của nhóm {group_name}."
                ),
            )
            tools.append(tool)

        if tools:
            self.router_query_engine = RouterQueryEngine.from_defaults(
                selector=LLMSingleSelector.from_defaults(),
                query_engine_tools=tools,
                verbose=False,
            )
        else:
            self.router_query_engine = None
            
    def ask(self, question: str, group: str = ALL_GROUPS) -> str:
        question = question.strip()
        if not question:
            return "Vui lòng nhập câu hỏi."

        # Chế độ chọn 1 nhóm riêng
        if group != ALL_GROUPS:
            query_engine = self.query_engines.get(group)
            if query_engine is None:
                return f"Không tìm thấy index cho nhóm '{group}'."

            response = query_engine.query(question)
            return str(response)

         # Chế độ tất cả folder
        else:
            query_engine = self.router_query_engine
            if query_engine is None:
                return "Chưa có tài liệu nào được tải lên."

            response = query_engine.query(question)
            return str(response)

    def ask_stream(self, question: str, group: str = ALL_GROUPS):
        question = question.strip()
        if not question:
            yield "Vui lòng nhập câu hỏi."
            return
        
        if group != ALL_GROUPS: # Chế độ chọn 1 nhóm riêng
            query_engine = self.query_engines.get(group)
            if query_engine is None:
                yield f"Không tìm thấy index cho nhóm '{group}'."
                return
            
        else: # Chế độ tất cả folder
            query_engine = self.router_query_engine
            if query_engine is None:
                yield "Chưa có tài liệu nào được tải lên."
                return

        response = query_engine.query(question)
        for chunk in response.response_gen:
            yield chunk

    def add_document(self, file_path: str):
        target = Path(file_path).resolve()
        group_dir = target.parent
        if group_dir.parent != self.data_dir:
            raise ValueError("Tài liệu phải nằm trong một nhóm.")

        self.rebuild_index()
        

    def delete_document(self, file_path: str):
        target = Path(file_path).resolve()
        target.unlink()
        self.rebuild_index()

