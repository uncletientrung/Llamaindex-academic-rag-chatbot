from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from pydantic import BaseModel
import shutil
from pipeline import Pipeline

class RAGEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pipeline = Pipeline(data_dir=self.data_dir)
        self.index = None
        self.query_engine = None

        self.rebuild_index()

    def rebuild_index(self):
        self.index = self.pipeline.build_index()
        if self.index is not None:
            self.query_engine =  self.index.as_query_engine(similarity_top_k=5)
        else:
            self.query_engine =None

    def add_document(self, file_path: str):
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        nodes = self.pipeline.process_documents(documents)
        if not nodes:
            return
        if self.index is None:
            self.index = VectorStoreIndex(
                nodes=nodes,
                storage_context=self.pipeline.get_storage(),
            )
        else:
            self.index.insert_nodes(nodes)

        self.query_engine = self.index.as_query_engine(similarity_top_k=5)
            
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
        if not target.is_relative_to(self.data_dir):
            raise ValueError("Đường dẫn tài liệu không hợp lệ.")

        if not target.is_file():
            raise FileNotFoundError("Không tìm thấy tài liệu.")

        target.unlink()
        self.rebuild_index()

