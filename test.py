from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from pydantic import BaseModel
import shutil
from ingestion import DocumentIngestionPipeline
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.tools import RetrieverTool
from src.promts.promt_qa import  QA_PROMPT
from constants import (
    ALL_GROUPS,
    SUPPORTED_EXTENSIONS,
    SIMILARITY_TOP_K
)
from postprocessors import NodePostprocessorFactory
from responsesynthesizer import ResponseSynthesizerFactory

   

class RAGService:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.ingest = DocumentIngestionPipeline(data_dir=self.data_dir)

        self.indices: dict[str, VectorStoreIndex] = {} # dict chứa các index cho từng folder
        self.query_engines = {} # dict chứa các query engine cho từng folder. Dùng cho chế độ chọn mục riêng để hỏi

        self.router_retriever = None # Cái này dùng cho chế độ chọn tất cả tài liệu
        self.router_query_engine = None # RetrieverQueryEngine + RouterRetriever => Hiểu ngầm là RouterQueryEngine (chứ k phải RouterQueryEngine )
        

        self.postprocessor_factory = NodePostprocessorFactory()
        self.synthesizer_factory = ResponseSynthesizerFactory()

        self.rebuild_index()

    def build_query_engine(self, retriever): # Có đủ node_postprocessors + res synthesizer + retriever có thể build thành query engine
        return RetrieverQueryEngine(
            retriever=retriever,
            node_postprocessors=self.postprocessor_factory.build(),
            response_synthesizer=self.synthesizer_factory.build(
                streaming=True
            ),
        )

    def rebuild_index(self):
        self.indices = self.ingest.build_indexes()
        self.query_engines = {}
        self.router_query_engine = None
        self.router_retriever = None

        retriever_tools  = [] 
        for group_name, index in self.indices.items(): #  query engine riêng cho mỗi folder
            retriever = index.as_retriever(
                similarity_top_k=SIMILARITY_TOP_K
            )
            self.query_engines[group_name] = self.build_query_engine(retriever)

            tool = RetrieverTool.from_defaults( # Các các option tool cho router retriever
                retriever= retriever,
                name=f"search_{group_name}",
                description=(
                    f"Tìm kiếm và trả lời câu hỏi dựa trên tài liệu thuộc nhóm {group_name}. "
                    f"Chọn công cụ này khi câu hỏi liên quan đến nội dung của nhóm {group_name}."
                )
            )
            retriever_tools.append(tool)

        if retriever_tools:
            self.router_retriever = RouterRetriever.from_defaults(
                selector=LLMSingleSelector.from_defaults(),
                retriever_tools=retriever_tools,
                verbose=False, # Hiển thị text hồng trên terminal đang chọn cái gì
            )

            self.router_query_engine = self.build_query_engine(self.router_retriever) # bỏ vào router query

            
    def ask(self, question: str, group: str = ALL_GROUPS) -> str:
        question = question.strip()
        if not question:
            return "Vui lòng nhập câu hỏi."

        # Chế độ chọn 1 nhóm riêng
        if group != ALL_GROUPS:
            query_engine = self.query_engines.get(group)
            if query_engine is None:
                return f"Không tìm thấy index cho nhóm '{group}'."

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

