from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from pathlib import Path
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
from src.promts.promt_extractor import (
    TITLE_NODE_PROMT,
    TITLE_COMBINE_PROMT,
    KEYWORD_PROMT,
)
from llama_index.core import StorageContext
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
            print(f"Bỏ qua thư mục không có file hợp lệ: {folder.name}")
            return []
        
        reader = SimpleDirectoryReader(
            input_files=files
        )
        return reader.load_data()

    def get_nodes(self, documents): # Hàm lấy các nodes đã extractor và embed
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
                    #   titleEx, keywordEx,
            # EntityExtractor(prediction_threshold=0.5),
            # SummaryExtractor(summaries=["prev", "self"]),
            # QuestionsAnsweredExtractor(questions=3),
            Settings.embed_model
        ]
        ingestion = IngestionPipeline(transformations=transform)
        nodes = ingestion.run(documents = documents)
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

    def build_indexes(self) -> dict[str, VectorStoreIndex]: # Hàm build các index
        self.indices = {}
        for folder in self.get_subfolders():
            print(f"Đang xử lý thư mục: {folder.name}")
            documents = self.load_documents(folder)
            if not documents:
                print(f"Bỏ qua thư mục rỗng: {folder.name}")
                continue

            nodes = self.get_nodes(documents)
            if not nodes:
                print(f"Không tạo được nodes: {folder.name}")
                continue
                        
            storage_context = self.get_storage()
            index = VectorStoreIndex(nodes= nodes, storage_context= storage_context)
            self.indices[folder.name] = index
            print(
                f"Đã tạo index: {folder.name} "
                f"({len(documents)} document, {len(nodes)} nodes)"
            )
        return self.indices