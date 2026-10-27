from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
from llama_index.core.schema import QueryBundle
from ingestion import DocumentIngestionPipeline
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import RouterRetriever
from llama_index.core.tools import RetrieverTool
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from promts.promt_qa import  QA_PROMPT, FALLBACK_PROMPT
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

    def rebuild_index(self, rebuild_groups: set[str] | None = None,):
        self.indices = self.ingest.build_indexes(rebuild_groups= rebuild_groups)
        self.query_engines = {}
        self.router_query_engine = None
        self.router_retriever = None

        retriever_tools  = [] 
        for group_name, index in self.indices.items(): #  query engine riêng cho mỗi folder
            filters = MetadataFilters( # Lọc theo tên folder của index
                filters=[
                    MetadataFilter(
                        key="folder_name",
                        value=group_name,
                    ),
                ]
            )

            retriever = index.as_retriever(similarity_top_k=SIMILARITY_TOP_K, filters= filters)
                
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
            )

            self.router_query_engine = self.build_query_engine(self.router_retriever) # bỏ vào router query

    def ask_stream(self, question: str, group: str = ALL_GROUPS, history: list | None = None,):
        question = question.strip()
        if not question:
            yield {"type": "sources", "sources": []}
            yield {"type": "token", "text": "Vui lòng nhập câu hỏi."}
            return
        
        if group != ALL_GROUPS: # Chế độ chọn 1 nhóm riêng
            query_engine = self.query_engines.get(group)
            if query_engine is None:
                yield {"type": "sources", "sources": []}
                yield {
                    "type": "token",
                    "text": f"Không tìm thấy index cho nhóm '{group}'.",
                }
                return
            
        else: # Chế độ tất cả folder
            query_engine = self.router_query_engine
            if query_engine is None:
                yield {"type": "sources", "sources": []}
                yield {"type": "token", "text": "Chưa có tài liệu nào được tải lên."}
                return

        query_bundle = QueryBundle(query_str=question) # SBERT Rerank cần lấy câu hỏi qua query_bundle.query_str để so sánh với từng đoạn tài liệu và xếp hạng lại.
        # Rerank bằng câu hỏi trước rồi mới dùng retrieval_query
        
        nodes = query_engine.retrieve(query_bundle)
  
        if not nodes:
            yield {"type": "sources", "sources": []}
            for chunk in self.fallback_stream(question):
                yield {"type": "token", "text": chunk}
            return

        yield { # Trả về các nodes sau khi rerank cho llm trả lời
            "type": "sources",
            "sources": self.extract_sources(nodes),
        }

        recent_history = (history or [])[-10:] # Lấy 10 cuộc hội thoại gần nhất
        history_text = ""
        for message in recent_history:
            role = 'Người dùng' if message.role.value == 'user' else 'Trợ lý'
            content = message.content or "" 
            history_text += f"{role}: {content}\n"

        if history_text:
            retrieval_query = f"""
            Lịch sử hội thoại:
            ---------------------
            {history_text}
            ---------------------
            Câu hỏi: 
            ---------------------
            {question}
            ---------------------
            """
        else:
            retrieval_query = question

        response = query_engine._response_synthesizer.synthesize(
            query=QueryBundle(query_str=retrieval_query),
            nodes=nodes,
        )
        print("================================= TẠO CÂU HỎI XONG =================================")
        # response = query_engine.query(question)
        for chunk in response.response_gen:
            print(chunk)
            yield {"type": "token", "text": chunk}

    def fallback_stream(self, question: str):
        prompt = FALLBACK_PROMPT.format(question=question)
        llm = self.synthesizer_factory.llm # Lấy llm trong synthesizer_factory
        response = llm.stream_complete(prompt)
        for chunk in response:
            if chunk.delta:
                yield chunk.delta

    def add_document(self, file_path: str):
        target = Path(file_path).resolve()
        group_dir = target.parent
        if group_dir.parent != self.data_dir:
            raise ValueError("Tài liệu phải nằm trong một nhóm.")
        
        self.rebuild_index(rebuild_groups={group_dir.name})
            
    def delete_document(self, file_path: str):
        target = Path(file_path).resolve()
        group_dir = target.parent
        target.unlink()

        self.rebuild_index(rebuild_groups={group_dir.name})

    def extract_sources(self, nodes): # Lấy các tt từ node để highlight
        sources = []
        seen = set()

        for item in nodes:
            node = item.node
            metadata = node.metadata or {}

            source = {
                "text": node.get_content(),
                "score":  float(item.score) if item.score is not None else None,
                "file_name": metadata.get("file_name"),
                "file_path": metadata.get("file_path"),
                "group": metadata.get("folder_name"),
                "page": metadata.get("page_label"),
            }

            key = (source["file_path"], source["page"], source["text"])
            if key in seen:
                continue

            seen.add(key)
            sources.append(source)

        return sources

    # Các hàm sử dụng để đánh giá
    def answer_with_context(self,question: str,group: str = ALL_GROUPS,):
        question = question.strip()

        if not question:
            raise ValueError("Câu hỏi không được để trống.")

        if group != ALL_GROUPS:
            query_engine = self.query_engines.get(group)
            if query_engine is None:
                raise ValueError(f"Không tìm thấy index cho nhóm '{group}'.")
        else:
            query_engine = self.router_query_engine
            if query_engine is None:
                raise ValueError("Chưa có tài liệu nào được tải lên.")

        # Truy xuất context qua toàn bộ retriever và postprocessor
        nodes = query_engine.retrieve(
            QueryBundle(query_str=question)
        )

        if not nodes:
            return {
                "query": question,
                "contexts": [],
                "response": "",
            }

        contexts = [
            node.node.get_content()
            for node in nodes
        ]

        # Sinh câu trả lời dựa trên chính các node đã truy xuất
        response = query_engine._response_synthesizer.synthesize(
            query=QueryBundle(query_str=question),
            nodes=nodes,
        )

        return {
            "query": question,
            "contexts": contexts,
            "response": str(response),
        }