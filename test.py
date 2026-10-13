from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from pydantic import BaseModel
import shutil
from pipeline import Pipeline
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector

class RAGEngine:
    ALL_GROUPS = "all"

    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pipeline = Pipeline(data_dir=self.data_dir)

        self.indices: dict[str, VectorStoreIndex] = {} # dict chứa các index cho từng folder
        self.query_engines = {} # dict chứa các query engine cho từng folder. Dùng cho chế độ chọn mục riêng để hỏi
        self.router_query_engine = None # Cái này dùng cho chế độ chọn tất cả tài liệu

        self.rebuild_index()

    def rebuild_index(self):
        self.indices = self.pipeline.build_indexes()

        for group_name, index in self.indices.items(): #  query engine riêng cho mỗi folder
            query_engine = index.as_query_engine(similarity_top_k=5)
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
        if group != self.ALL_GROUPS:

            query_engine = self.query_engines.get(group)
            if query_engine is None:
                return f"Không tìm thấy index cho nhóm '{group}'."

            response = query_engine.query(question)
            return str(response)

         # Chế độ tất cả folder
        if self.router_query_engine is None:
            return "Chưa có tài liệu nào được tải lên."

        response = self.router_query_engine.query(question)
        return str(response)

    def add_document(self, file_path: str):
        target = Path(file_path).resolve()

        if not target.is_relative_to(self.data_dir):
            raise ValueError("Đường dẫn tài liệu không hợp lệ.")

        if not target.is_file():
            raise FileNotFoundError("Không tìm thấy tài liệu.")

        if target.suffix.lower() not in self.pipeline.SUPPORTED_EXTENSIONS:
            raise ValueError("Định dạng file không được hỗ trợ.")

        # Tài liệu thuộc folder cha trực tiếp trong data/
        group_dir = target.parent

        if group_dir.parent != self.data_dir:
            raise ValueError("Tài liệu phải nằm trong một nhóm.")
        
        self.rebuild_index()
        

    def delete_document(self, file_path: str):
        target = Path(file_path).resolve()
        if not target.is_relative_to(self.data_dir):
            raise ValueError("Đường dẫn tài liệu không hợp lệ.")

        if not target.is_file():
            raise FileNotFoundError("Không tìm thấy tài liệu.")

        target.unlink()
        self.rebuild_index()

