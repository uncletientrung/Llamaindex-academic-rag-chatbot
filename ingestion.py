from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
import shutil
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
    KeywordExtractor,
)
from llama_index.extractors.entity import EntityExtractor
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from promts.promt_extractor import (
    TITLE_NODE_PROMT,
    TITLE_COMBINE_PROMT,
    KEYWORD_PROMT,
)
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core.vector_stores import SimpleVectorStore
from constants import (
    SUPPORTED_EXTENSIONS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    EMBEDDING_MODEL
)

class DocumentIngestionPipeline:
    def __init__(self, data_dir="data"):
        # =========================
        # 1. Cấu hình
        # =========================
        Settings.llm = Ollama(model="qwen2.5:3b",request_timeout=120.0,)
        Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)

        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.storage_dir = self.data_dir.parent / "storage"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.indices: dict[str, VectorStoreIndex]={}

    def get_subfolders(self) -> list[Path]:
        return sorted([
            path
            for path in self.data_dir.iterdir()
            if path.is_dir()
            ],key=lambda path: path.name.lower()
        )
    
    def get_files(self, folder: Path) -> list[str]:
        return [
            str(path)
            for path in folder.rglob("*")
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    def load_documents(self, folder: Path): # Load các doc từ file
        files = self.get_files(folder)
        if not files:
            print(f"Bỏ qua thư mục không có file: {folder.name}")
            return []
        
        reader = SimpleDirectoryReader(
            input_files=files
        )
        return reader.load_data()

    def get_nodes(self, documents, folder_name: str): # Hàm lấy các nodes đã extractor và embed
        split = SentenceSplitter(chunk_size= DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP)
        titleEx = TitleExtractor(
            llm=Settings.llm,
            nodes=5,
            node_template=TITLE_NODE_PROMT,
            combine_template=TITLE_COMBINE_PROMT,
        )
        keywordEx = KeywordExtractor(
            llm= Settings.llm,
            keywords=5,
            prompt_template= KEYWORD_PROMT
        )

        transform = [ split,
                    #   titleEx,
                    #  keywordEx,
            # EntityExtractor(prediction_threshold=0.5),
            # SummaryExtractor(summaries=["prev", "self"]),
            # QuestionsAnsweredExtractor(questions=3),
            Settings.embed_model
        ]
        ingestion = IngestionPipeline(transformations=transform)
        nodes = ingestion.run(documents = documents)

        for node in nodes:
            node.metadata["folder_name"] = folder_name 
        return nodes

    def get_storage(self): # Hàm định nghĩa storage
        storage = StorageContext(
            docstore=SimpleDocumentStore(),
            index_store=SimpleIndexStore(),
            vector_stores={
                "default": SimpleVectorStore()
            },
            graph_store=SimpleGraphStore(),
        )
        return storage

    
    def build_indexes(self, rebuild_groups: set[str] | None = None,) -> dict[str, VectorStoreIndex]:
        self.indices = {}

        rebuild_groups = rebuild_groups or set()

        folders = self.get_subfolders()
        current_groups = {folder.name for folder in folders}

        # Xóa storage của những nhóm tài liệu đã bị xóa
        for saved_storage_dir in self.storage_dir.iterdir(): # Lấy các folder và file đã lưu vào storage
            if saved_storage_dir.is_dir() and saved_storage_dir.name not in current_groups:
                shutil.rmtree(saved_storage_dir)

        for folder in folders:
            group_name = folder.name
            persist_dir = self.storage_dir / group_name
            print(f"Đang xử lý nhóm: {group_name}")

            # Load lại index đã lưu
            if (persist_dir.is_dir() and group_name not in rebuild_groups):
                try:
                    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir) )
                    index = load_index_from_storage(storage_context)
                    self.indices[group_name] = index
                    print(f"Đã load lại index từ storage: {group_name}")
                    continue

                except Exception as ex:
                    print(
                        f"Không load được {group_name}: {ex}. "
                        "Sẽ build lại."
                    )
                    shutil.rmtree(persist_dir, ignore_errors=True)

            # Chưa có storage hoặc cần cập nhật index
            documents = self.load_documents(folder)
            if not documents:
                print(f"Bỏ qua thư mục rỗng: {folder.name}")
                continue

            nodes = self.get_nodes(documents, folder_name=group_name)
            if not nodes:
                print(f"Không tạo được nodes: {group_name}")
                continue

            # Mỗi nhóm có một storage riêng
            storage_context = self.get_storage()
            index = VectorStoreIndex(
                nodes=nodes,
                storage_context=storage_context,
            )

            # Lưu Node, vector và index xuống ổ đĩa
            persist_dir.mkdir(parents=True, exist_ok=True)
            index.storage_context.persist(
                persist_dir=str(persist_dir)
            )

            self.indices[group_name] = index

            print(
                f"Đã build và lưu index: {group_name} "
                f"({len(documents)} documents, {len(nodes)} nodes)"
            )

        return self.indices